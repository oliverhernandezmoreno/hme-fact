from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models import DTE, DTEEvent, DTEEventType, DTEStatus, DTEStatusHistory, DTETransmission
from app.modules.integrations.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderHTTPError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    TaxIntegrationError,
    TaxRejectionError,
    XMLInvalidError,
)
from app.modules.integrations.providers import BaseTaxProvider
from app.modules.integrations.repositories import (
    DTEStatusHistoryRepository,
    DTETransmissionRepository,
)
from app.modules.integrations.schemas.tax import (
    DTEStatusResponse,
    DTETransmissionRead,
    TaxProviderContext,
    TaxProviderResponse,
    TaxSendRequest,
)
from app.modules.integrations.services.provider_factory import TaxProviderFactory
from app.modules.xml.validators.xml_validator import XmlValidatorService
from app.repositories.dte import DTERepository

logger = logging.getLogger(__name__)


class TaxIntegrationService:
    sendable_statuses = {
        DTEStatus.GENERATED,
        DTEStatus.SIGNED,
        DTEStatus.ERROR,
    }

    def __init__(
        self,
        session: AsyncSession,
        *,
        settings: Settings | None = None,
        provider: BaseTaxProvider | None = None,
        xml_validator: XmlValidatorService | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.provider = provider or TaxProviderFactory(self.settings).create()
        self.xml_validator = xml_validator or XmlValidatorService()
        self.dte_repository = DTERepository(session)
        self.transmission_repository = DTETransmissionRepository(session)
        self.history_repository = DTEStatusHistoryRepository(session)

    async def send_dte(self, *, dte_id: uuid.UUID, company_id: uuid.UUID) -> DTEStatusResponse:
        dte = await self._get_dte(dte_id=dte_id, company_id=company_id)
        xml_content = await self._get_xml_content(dte)
        self._validate_sendable_status(dte)
        self._validate_xml(xml_content)

        request = TaxSendRequest(
            xml_content=xml_content,
            context=TaxProviderContext(
                company_id=dte.company_id,
                dte_id=dte.id,
                company_rut=dte.company.rut,
                dte_type=dte.dte_type,
                folio=dte.folio,
            ),
        )
        request_payload = self._request_audit_payload(dte=dte, xml_content=xml_content)
        previous_status = dte.status

        try:
            provider_response = await self.provider.send_dte(request)
        except TaxIntegrationError as exc:
            error_status = (
                DTEStatus.REJECTED if isinstance(exc, TaxRejectionError) else DTEStatus.ERROR
            )
            transmission = DTETransmission(
                dte_id=dte.id,
                provider=self.provider.provider_name,
                external_track_id=self._track_id_from_payload(exc.payload),
                request_payload=request_payload,
                response_payload=exc.payload,
                status=error_status.value,
                sent_at=datetime.now(UTC),
            )
            self.transmission_repository.add(transmission)
            self._apply_dte_status(dte, error_status)
            self._record_status_change(
                dte=dte,
                previous_status=previous_status,
                new_status=error_status,
                provider_response=exc.payload,
            )
            self._record_event(
                dte=dte,
                event_type=self._event_for_status(error_status),
                message=exc.message,
                payload=self._exception_payload(exc),
            )
            await self.session.commit()
            await self.session.refresh(transmission)
            logger.warning(
                "DTE send failed",
                extra={"dte_id": str(dte.id), "provider": self.provider.provider_name},
            )
            raise

        transmission = DTETransmission(
            dte_id=dte.id,
            provider=self.provider.provider_name,
            external_track_id=provider_response.track_id,
            request_payload=request_payload,
            response_payload=provider_response.raw_response,
            status=provider_response.status.value,
            sent_at=datetime.now(UTC),
        )
        self.transmission_repository.add(transmission)
        dte.sii_track_id = provider_response.track_id
        dte.sii_response = provider_response.raw_response
        dte.sent_at = datetime.now(UTC)
        self._record_status_change(
            dte=dte,
            previous_status=previous_status,
            new_status=provider_response.status,
            provider_response=provider_response.raw_response,
        )
        self._record_event(
            dte=dte,
            event_type=DTEEventType.SENT_TO_SII,
            message="DTE sent to active tax provider",
            payload=provider_response.raw_response,
        )
        self._apply_dte_status(dte, provider_response.status)
        await self.session.commit()
        await self.session.refresh(transmission)
        logger.info(
            "DTE sent to tax provider",
            extra={
                "dte_id": str(dte.id),
                "provider": self.provider.provider_name,
                "track_id": provider_response.track_id,
                "status": provider_response.status.value,
            },
        )
        return self._response(
            dte=dte,
            provider_response=provider_response,
            transmission=transmission,
        )

    async def get_status(self, *, dte_id: uuid.UUID, company_id: uuid.UUID) -> DTEStatusResponse:
        dte = await self._get_dte(dte_id=dte_id, company_id=company_id)
        transmission = await self.transmission_repository.get_latest_with_track_id(dte.id)
        track_id = dte.sii_track_id or (transmission.external_track_id if transmission else None)
        if not track_id:
            raise ProviderConfigurationError(
                "DTE has no external tracking id",
                provider=self.provider.provider_name,
            )

        provider_response = await self.provider.get_status(track_id)
        previous_status = dte.status
        self._apply_dte_status(dte, provider_response.status)
        dte.sii_response = provider_response.raw_response
        if provider_response.track_id:
            dte.sii_track_id = provider_response.track_id
        if dte.status == DTEStatus.ACCEPTED and dte.accepted_at is None:
            dte.accepted_at = datetime.now(UTC)

        if transmission is not None:
            transmission.status = provider_response.status.value
            transmission.response_payload = provider_response.raw_response
            transmission.last_check_at = datetime.now(UTC)

        self._record_status_change(
            dte=dte,
            previous_status=previous_status,
            new_status=provider_response.status,
            provider_response=provider_response.raw_response,
        )
        self._record_event(
            dte=dte,
            event_type=self._event_for_status(provider_response.status),
            message="DTE status checked against active tax provider",
            payload=provider_response.raw_response,
        )
        await self.session.commit()
        if transmission is not None:
            await self.session.refresh(transmission)
        logger.info(
            "DTE provider status updated",
            extra={
                "dte_id": str(dte.id),
                "provider": self.provider.provider_name,
                "track_id": track_id,
                "status": provider_response.status.value,
            },
        )
        return self._response(
            dte=dte,
            provider_response=provider_response,
            transmission=transmission,
        )

    async def _get_dte(self, *, dte_id: uuid.UUID, company_id: uuid.UUID) -> DTE:
        dte = await self.dte_repository.get_for_tax_integration(
            dte_id=dte_id,
            company_id=company_id,
        )
        if dte is None:
            raise LookupError("DTE not found")
        return dte

    async def _get_xml_content(self, dte: DTE) -> str:
        xml_document = dte.xml_documents[0] if dte.xml_documents else None
        if xml_document is None:
            raise XMLInvalidError(
                "DTE XML has not been generated",
                provider=self.provider.provider_name,
                retryable=False,
            )
        return xml_document.xml_content

    def _validate_sendable_status(self, dte: DTE) -> None:
        if dte.status not in self.sendable_statuses:
            raise TaxIntegrationError(
                f"DTE cannot be sent from status {dte.status.value}",
                provider=self.provider.provider_name,
                retryable=False,
            )

    def _validate_xml(self, xml_content: str) -> None:
        try:
            self.xml_validator.validate_well_formed(xml_content)
            self.xml_validator.validate_required_nodes(xml_content)
        except Exception as exc:
            raise XMLInvalidError(
                "DTE XML is invalid",
                provider=self.provider.provider_name,
                payload={"error": str(exc)},
                retryable=False,
            ) from exc

    def _apply_dte_status(self, dte: DTE, status: DTEStatus) -> None:
        dte.status = status

    def _record_status_change(
        self,
        *,
        dte: DTE,
        previous_status: DTEStatus | None,
        new_status: DTEStatus,
        provider_response: dict[str, Any] | None,
    ) -> None:
        self.history_repository.add(
            DTEStatusHistory(
                dte_id=dte.id,
                previous_status=previous_status.value if previous_status else None,
                new_status=new_status.value,
                provider_response=provider_response,
            )
        )

    def _record_event(
        self,
        *,
        dte: DTE,
        event_type: DTEEventType,
        message: str,
        payload: dict[str, Any] | None,
    ) -> None:
        self.session.add(
            DTEEvent(
                dte_id=dte.id,
                event_type=event_type,
                message=message,
                actor="tax-integration",
                payload=payload,
            )
        )

    def _event_for_status(self, status: DTEStatus) -> DTEEventType:
        if status == DTEStatus.ACCEPTED:
            return DTEEventType.SII_ACCEPTED
        if status == DTEStatus.REJECTED:
            return DTEEventType.SII_REJECTED
        if status == DTEStatus.ERROR:
            return DTEEventType.SII_ERROR
        return DTEEventType.SII_STATUS_CHECKED

    def _request_audit_payload(self, *, dte: DTE, xml_content: str) -> dict[str, object]:
        return {
            "dte_id": str(dte.id),
            "company_id": str(dte.company_id),
            "company_rut": dte.company.rut,
            "dte_type": dte.dte_type,
            "folio": dte.folio,
            "xml_sha256": hashlib.sha256(xml_content.encode("utf-8")).hexdigest(),
            "xml_size_bytes": len(xml_content.encode("utf-8")),
        }

    def _track_id_from_payload(self, payload: dict[str, Any]) -> str | None:
        value = (
            payload.get("track_id") or payload.get("external_track_id") or payload.get("trackId")
        )
        return str(value) if value is not None else None

    def _exception_payload(self, exc: TaxIntegrationError) -> dict[str, object]:
        return {
            "message": exc.message,
            "provider": exc.provider,
            "status_code": exc.status_code,
            "retryable": exc.retryable,
            "payload": exc.payload,
            "error_type": exc.__class__.__name__,
        }

    def _response(
        self,
        *,
        dte: DTE,
        provider_response: TaxProviderResponse,
        transmission: DTETransmission | None,
    ) -> DTEStatusResponse:
        return DTEStatusResponse(
            dte_id=dte.id,
            status=dte.status,
            provider=self.provider.provider_name,
            external_track_id=provider_response.track_id,
            provider_status=provider_response.provider_status,
            detail=provider_response.detail,
            errors=provider_response.errors,
            transmission=DTETransmissionRead.model_validate(transmission) if transmission else None,
        )


def http_status_for_tax_error(exc: TaxIntegrationError) -> int:
    if isinstance(exc, ProviderConfigurationError):
        return 400
    if isinstance(exc, XMLInvalidError):
        return 422
    if isinstance(exc, ProviderAuthenticationError):
        return 502
    if isinstance(exc, ProviderRateLimitError):
        return 429
    if isinstance(exc, ProviderTimeoutError):
        return 504
    if isinstance(exc, ProviderHTTPError):
        return 502
    return 409
