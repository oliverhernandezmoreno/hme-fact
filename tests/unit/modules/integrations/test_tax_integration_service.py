from __future__ import annotations

import uuid
from datetime import date
from typing import Any

import pytest

from app.models import DTE, Company, DTEStatus, DTETransmission, DTEXml, DTEXmlType
from app.modules.integrations.providers import BaseTaxProvider
from app.modules.integrations.schemas import (
    CompanyInfoResponse,
    ProviderHealthResponse,
    TaxProviderResponse,
    TaxSendRequest,
)
from app.modules.integrations.services import TaxIntegrationService

pytestmark = [pytest.mark.unit]


class FakeTaxProvider(BaseTaxProvider):
    provider_name = "fake"

    async def send_dte(self, request: TaxSendRequest) -> TaxProviderResponse:
        return TaxProviderResponse(
            provider=self.provider_name,
            status=DTEStatus.SENT,
            provider_status="RECIBIDO",
            track_id="TRACK-1",
            raw_response={"track_id": "TRACK-1", "estado": "RECIBIDO"},
        )

    async def get_status(self, track_id: str) -> TaxProviderResponse:
        return TaxProviderResponse(
            provider=self.provider_name,
            status=DTEStatus.ACCEPTED,
            provider_status="ACEPTADO",
            track_id=track_id,
            raw_response={"track_id": track_id, "estado": "ACEPTADO"},
        )

    async def validate_connection(self) -> ProviderHealthResponse:
        return ProviderHealthResponse(provider=self.provider_name, ok=True)

    async def generate_pdf(self, track_id: str) -> bytes:
        return b"%PDF"

    async def get_company_info(self, rut: str) -> CompanyInfoResponse:
        return CompanyInfoResponse(provider=self.provider_name, rut=rut)


class NoopXmlValidator:
    def validate_well_formed(self, xml_content: str) -> None:
        return None

    def validate_required_nodes(self, xml_content: str) -> None:
        return None


class FakeSession:
    def __init__(self) -> None:
        self.added: list[Any] = []
        self.commits = 0

    def add(self, entity: Any) -> None:
        self.added.append(entity)

    async def commit(self) -> None:
        self.commits += 1

    async def refresh(self, entity: Any) -> None:
        return None


class FakeDTERepository:
    def __init__(self, dte: DTE | None) -> None:
        self.dte = dte

    async def get_for_tax_integration(
        self,
        *,
        dte_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> DTE | None:
        if self.dte is None:
            return None
        if self.dte.id == dte_id and self.dte.company_id == company_id:
            return self.dte
        return None


class FakeTransmissionRepository:
    def __init__(self, transmission: DTETransmission | None = None) -> None:
        self.transmissions: list[DTETransmission] = []
        self.transmission = transmission

    def add(self, entity: DTETransmission) -> DTETransmission:
        entity.id = uuid.uuid4()
        self.transmissions.append(entity)
        self.transmission = entity
        return entity

    async def get_latest_with_track_id(self, dte_id: uuid.UUID) -> DTETransmission | None:
        return self.transmission


class FakeHistoryRepository:
    def __init__(self) -> None:
        self.history: list[Any] = []

    def add(self, entity: Any) -> Any:
        self.history.append(entity)
        return entity


def _dte(*, status: DTEStatus, with_xml: bool = True) -> DTE:
    company_id = uuid.uuid4()
    dte = DTE(
        id=uuid.uuid4(),
        company_id=company_id,
        customer_id=uuid.uuid4(),
        dte_type=33,
        folio=10,
        status=status,
        issue_date=date(2026, 5, 22),
        net_amount=10000,
        exempt_amount=0,
        tax_amount=1900,
        total_amount=11900,
    )
    dte.company = Company(id=company_id, rut="76123456-7", legal_name="Demo SpA")
    if with_xml:
        dte.xml_documents = [
            DTEXml(
                dte_id=dte.id,
                xml_type=DTEXmlType.UNSIGNED_DTE,
                xml_content="<DTE />",
            )
        ]
    return dte


def _service(dte: DTE | None, transmission: DTETransmission | None = None) -> TaxIntegrationService:
    service = TaxIntegrationService(
        FakeSession(),  # type: ignore[arg-type]
        provider=FakeTaxProvider(),
        xml_validator=NoopXmlValidator(),
    )
    service.dte_repository = FakeDTERepository(dte)  # type: ignore[assignment]
    service.transmission_repository = FakeTransmissionRepository(transmission)  # type: ignore[assignment]
    service.history_repository = FakeHistoryRepository()  # type: ignore[assignment]
    return service


async def test_tax_integration_service_sends_dte_and_records_tracking() -> None:
    dte = _dte(status=DTEStatus.GENERATED)

    service = _service(dte)
    result = await service.send_dte(dte_id=dte.id, company_id=dte.company_id)

    assert result.status == DTEStatus.SENT
    assert result.external_track_id == "TRACK-1"
    assert dte.status == DTEStatus.SENT
    assert dte.sii_track_id == "TRACK-1"
    assert len(service.transmission_repository.transmissions) == 1
    assert len(service.history_repository.history) == 1


async def test_tax_integration_service_updates_status_from_provider() -> None:
    dte = _dte(status=DTEStatus.SENT)
    dte.sii_track_id = "TRACK-1"

    result = await _service(dte).get_status(dte_id=dte.id, company_id=dte.company_id)

    assert result.status == DTEStatus.ACCEPTED
    assert dte.status == DTEStatus.ACCEPTED
    assert dte.accepted_at is not None


async def test_tax_integration_service_requires_tenant_dte() -> None:
    with pytest.raises(LookupError):
        await _service(None).send_dte(dte_id=uuid.uuid4(), company_id=uuid.uuid4())
