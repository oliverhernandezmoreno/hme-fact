from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(frozen=True, slots=True)
class SIIUploadResult:
    track_id: str
    status: str


class SIIWrapperClient:
    def __init__(
        self,
        *,
        base_url: str,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    async def upload_dte_xml(self, xml_content: str) -> SIIUploadResult:
        if self.http_client is not None:
            return await self._upload_with_client(self.http_client, xml_content)

        async with httpx.AsyncClient(timeout=30) as client:
            return await self._upload_with_client(client, xml_content)

    async def _upload_with_client(
        self,
        client: httpx.AsyncClient,
        xml_content: str,
    ) -> SIIUploadResult:
        response = await client.post(
            f"{self.base_url}/dte/upload",
            content=xml_content.encode("utf-8"),
            headers={"Content-Type": "application/xml; charset=utf-8"},
        )
        response.raise_for_status()
        payload = response.json()
        return SIIUploadResult(
            track_id=str(payload["track_id"]),
            status=str(payload["status"]),
        )


class SimpleAPIClient:
    def __init__(
        self,
        *,
        base_url: str,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    async def get_dte_status(self, track_id: str) -> dict[str, str]:
        if self.http_client is not None:
            return await self._get_status_with_client(self.http_client, track_id)

        async with httpx.AsyncClient(timeout=30) as client:
            return await self._get_status_with_client(client, track_id)

    async def _get_status_with_client(
        self,
        client: httpx.AsyncClient,
        track_id: str,
    ) -> dict[str, str]:
        response = await client.get(f"{self.base_url}/dte/status/{track_id}")
        response.raise_for_status()
        payload = response.json()
        return {str(key): str(value) for key, value in payload.items()}
