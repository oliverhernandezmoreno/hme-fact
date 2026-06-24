from __future__ import annotations

import logging
import time
from collections.abc import Mapping
from typing import Any

import httpx

from app.modules.integrations.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderHTTPError,
    ProviderRateLimitError,
    ProviderTemporaryError,
    ProviderTimeoutError,
)
from app.modules.integrations.utils.retry import retry_async

logger = logging.getLogger(__name__)


class SimpleApiHttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float,
        max_retries: int,
        backoff_base_seconds: float,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base_seconds = backoff_base_seconds
        self.http_client = http_client

    async def post_json(
        self,
        path: str,
        *,
        json_payload: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> tuple[dict[str, Any], int]:
        return await retry_async(
            lambda: self._request_json("POST", path, json_payload=json_payload, headers=headers),
            max_retries=self.max_retries,
            backoff_base_seconds=self.backoff_base_seconds,
        )

    async def get_json(self, path: str) -> tuple[dict[str, Any], int]:
        return await retry_async(
            lambda: self._request_json("GET", path),
            max_retries=self.max_retries,
            backoff_base_seconds=self.backoff_base_seconds,
        )

    async def get_bytes(self, path: str) -> bytes:
        return await retry_async(
            lambda: self._request_bytes("GET", path),
            max_retries=self.max_retries,
            backoff_base_seconds=self.backoff_base_seconds,
        )

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json_payload: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[dict[str, Any], int]:
        response, duration_ms = await self._send(
            method,
            path,
            json_payload=json_payload,
            headers=headers,
        )
        payload = self._json_payload(response)
        self._raise_for_provider_error(response, payload)
        return payload, duration_ms

    async def _request_bytes(self, method: str, path: str) -> bytes:
        response, _duration_ms = await self._send(method, path)
        content_type = response.headers.get("content-type", "")
        payload = (
            self._json_payload(response)
            if content_type.startswith("application/json")
            else {}
        )
        self._raise_for_provider_error(response, payload)
        return response.content

    async def _send(
        self,
        method: str,
        path: str,
        *,
        json_payload: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[httpx.Response, int]:
        request_headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
            **dict(headers or {}),
        }
        started = time.perf_counter()
        url = f"{self.base_url}{path}"
        try:
            if self.http_client is not None:
                response = await self.http_client.request(
                    method,
                    url,
                    json=json_payload,
                    headers=request_headers,
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method,
                        url,
                        json=json_payload,
                        headers=request_headers,
                    )
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(
                "Tax provider request timed out",
                provider="simpleapi",
                retryable=True,
            ) from exc
        except httpx.TransportError as exc:
            raise ProviderConnectionError(
                "Tax provider connection failed",
                provider="simpleapi",
                retryable=True,
            ) from exc

        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Tax provider HTTP exchange",
            extra={
                "provider": "simpleapi",
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response, duration_ms

    def _json_payload(self, response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError:
            return {"raw_body": response.text}
        return payload if isinstance(payload, dict) else {"data": payload}

    def _raise_for_provider_error(
        self,
        response: httpx.Response,
        payload: dict[str, Any],
    ) -> None:
        if response.status_code < 400:
            return

        message = str(payload.get("message") or payload.get("error") or response.reason_phrase)
        retryable = response.status_code in {408, 429, 500, 502, 503, 504}
        kwargs = {
            "provider": "simpleapi",
            "status_code": response.status_code,
            "payload": payload,
            "retryable": retryable,
        }
        if response.status_code in {401, 403}:
            raise ProviderAuthenticationError(message, **kwargs)
        if response.status_code == 429:
            raise ProviderRateLimitError(message, **kwargs)
        if response.status_code in {408, 500, 502, 503, 504}:
            raise ProviderTemporaryError(message, **kwargs)
        raise ProviderHTTPError(message, **kwargs)
