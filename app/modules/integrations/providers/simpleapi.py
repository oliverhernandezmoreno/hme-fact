from __future__ import annotations

from typing import Any

from app.models.enums import DTEStatus
from app.modules.integrations.clients import SimpleApiHttpClient
from app.modules.integrations.exceptions import ProviderHTTPError, TaxRejectionError
from app.modules.integrations.providers.base import BaseTaxProvider
from app.modules.integrations.schemas import (
    CompanyInfoResponse,
    ProviderHealthResponse,
    TaxProviderErrorDetail,
    TaxProviderResponse,
    TaxSendRequest,
)
from app.modules.integrations.utils.status import normalize_tax_status


class SimpleApiProvider(BaseTaxProvider):
    provider_name = "simpleapi"

    def __init__(self, client: SimpleApiHttpClient) -> None:
        self.client = client

    async def send_dte(self, request: TaxSendRequest) -> TaxProviderResponse:
        payload = {
            "xml": request.xml_content,
            "company_rut": request.context.company_rut,
            "dte_type": request.context.dte_type,
            "folio": request.context.folio,
            "metadata": {
                "company_id": str(request.context.company_id),
                "dte_id": str(request.context.dte_id),
            },
        }
        try:
            response, duration_ms = await self.client.post_json("/dte/send", json_payload=payload)
        except ProviderHTTPError as exc:
            status = normalize_tax_status(
                exc.payload.get("status") or exc.payload.get("estado") or exc.payload.get("state")
            )
            if status in {DTEStatus.REJECTED, DTEStatus.ERROR}:
                raise TaxRejectionError(
                    exc.message,
                    provider=self.provider_name,
                    status_code=exc.status_code,
                    payload=exc.payload,
                    retryable=False,
                ) from exc
            raise
        normalized = self._normalize_response(response, duration_ms=duration_ms)
        if normalized.status in {DTEStatus.REJECTED, DTEStatus.ERROR}:
            raise TaxRejectionError(
                normalized.detail or "DTE rejected by tax provider",
                provider=self.provider_name,
                payload=response,
                retryable=False,
            )
        return normalized

    async def get_status(self, track_id: str) -> TaxProviderResponse:
        response, duration_ms = await self.client.get_json(f"/dte/status/{track_id}")
        return self._normalize_response(
            response,
            duration_ms=duration_ms,
            fallback_track_id=track_id,
        )

    async def validate_connection(self) -> ProviderHealthResponse:
        response, _duration_ms = await self.client.get_json("/health")
        ok_value = response.get("ok", response.get("status", "ok"))
        return ProviderHealthResponse(
            provider=self.provider_name,
            ok=str(ok_value).lower() in {"ok", "true", "healthy"},
            raw_response=response,
        )

    async def generate_pdf(self, track_id: str) -> bytes:
        return await self.client.get_bytes(f"/dte/pdf/{track_id}")

    async def get_company_info(self, rut: str) -> CompanyInfoResponse:
        response, _duration_ms = await self.client.get_json(f"/companies/{rut}")
        return CompanyInfoResponse(
            provider=self.provider_name,
            rut=str(response.get("rut", rut)),
            legal_name=self._optional_str(
                response.get("legal_name") or response.get("razon_social")
            ),
            giro=self._optional_str(response.get("giro")),
            raw_response=response,
        )

    def _normalize_response(
        self,
        payload: dict[str, Any],
        *,
        duration_ms: int,
        fallback_track_id: str | None = None,
    ) -> TaxProviderResponse:
        track_id = self._optional_str(
            payload.get("track_id")
            or payload.get("external_track_id")
            or payload.get("trackId")
            or payload.get("id")
            or fallback_track_id
        )
        provider_status = str(
            payload.get("status")
            or payload.get("estado")
            or payload.get("sii_status")
            or payload.get("state")
            or "sent"
        )
        status = normalize_tax_status(provider_status)
        return TaxProviderResponse(
            provider=self.provider_name,
            status=status,
            provider_status=provider_status,
            track_id=track_id,
            detail=self._optional_str(
                payload.get("detail") or payload.get("message") or payload.get("glosa")
            ),
            errors=self._normalize_errors(payload),
            raw_response=payload,
            duration_ms=duration_ms,
        )

    def _normalize_errors(self, payload: dict[str, Any]) -> list[TaxProviderErrorDetail]:
        raw_errors = payload.get("errors") or payload.get("errores") or []
        if isinstance(raw_errors, str):
            raw_errors = [raw_errors]
        if not isinstance(raw_errors, list):
            raw_errors = [raw_errors]

        errors: list[TaxProviderErrorDetail] = []
        for error in raw_errors:
            if isinstance(error, dict):
                errors.append(
                    TaxProviderErrorDetail(
                        code=self._optional_str(error.get("code") or error.get("codigo")),
                        message=str(error.get("message") or error.get("glosa") or error),
                        field=self._optional_str(error.get("field") or error.get("campo")),
                        raw=error,
                    )
                )
            else:
                errors.append(TaxProviderErrorDetail(message=str(error)))
        return errors

    def _optional_str(self, value: object) -> str | None:
        if value is None:
            return None
        return str(value)
