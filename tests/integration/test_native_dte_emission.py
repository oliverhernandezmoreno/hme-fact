from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DTE, CAFFile, Certificate, Company, Customer
from app.models.enums import DTEStatus

pytestmark = [pytest.mark.integration]


@pytest.fixture
async def seeded_certificates_and_cafs(
    db_session: AsyncSession,
    company: Company,
):
    # Seed mock cert and CAFs for the fixture's company
    from app.cli.seed_certs_and_caf import generate_mock_caf_xml, generate_mock_pfx
    from app.services.certificate_security import CertificateSecurityService

    security_service = CertificateSecurityService()
    pfx_bytes, password = generate_mock_pfx()
    metadata = security_service.extract_metadata(pfx_bytes, password)

    encrypted_pfx = security_service.encrypt_data(pfx_bytes)
    encrypted_password = security_service.encrypt_data(password.encode("utf-8"))

    cert = Certificate(
        company_id=company.id,
        common_name=metadata["common_name"],
        serial_number=metadata["serial_number"],
        encrypted_pfx=encrypted_pfx,
        encrypted_password=encrypted_password,
        valid_from=metadata["valid_from"],
        valid_until=metadata["valid_until"],
        is_active=True,
    )
    db_session.add(cert)

    caf_xml, private_key = generate_mock_caf_xml(company.rut, company.legal_name, 33)
    caf = CAFFile(
        company_id=company.id,
        dte_type=33,
        folio_from=1,
        folio_to=1000,
        current_folio=1,
        authorization_date=metadata["valid_from"].date(),
        xml_content=caf_xml,
        private_key=private_key,
    )
    db_session.add(caf)
    await db_session.commit()

    return cert, caf


@pytest.mark.asyncio
@patch("app.services.sii.client.SIIWebServicesClient.get_token", new_callable=AsyncMock)
@patch("app.services.sii.client.SIIWebServicesClient.enviar_dte", new_callable=AsyncMock)
async def test_native_dte_emission_flow(
    mock_enviar,
    mock_get_token,
    client: AsyncClient,
    company: Company,
    customer: Customer,
    tenant_headers: dict[str, str],
    seeded_certificates_and_cafs,
) -> None:
    # Mock SII responses
    mock_get_token.return_value = "fake_token_123"
    mock_enviar.return_value = "track_id_98765"

    # 1. Create DTE draft via API
    payload = {
        "dte_type": 33,
        "customer_id": str(customer.id),
        "issue_date": "2026-06-26",
        "items": [
            {
                "description": "Servicio de Consultoria",
                "quantity": 1.0,
                "unit": "UN",
                "unit_price": 500000.0,
                "discount_amount": 0.0,
                "tax_exempt": False,
            }
        ],
    }

    create_resp = await client.post("/api/v1/dte", json=payload, headers=tenant_headers)
    assert create_resp.status_code == 201, create_resp.text
    dte_data = create_resp.json()
    dte_id = dte_data["id"]

    # 2. Call the emit endpoint (calls emit_dte_task.delay under the hood)
    with patch("app.workers.tasks.dte_emission.emit_dte_task.delay") as mock_delay:
        emit_resp = await client.post(f"/api/v1/dte/{dte_id}/emit", headers=tenant_headers)
        assert emit_resp.status_code == 202, emit_resp.text
        assert emit_resp.json()["status"] == "QUEUED"
        mock_delay.assert_called_once_with(dte_id)

    # 3. Now run the async emission logic directly
    from uuid import UUID

    from app.workers.tasks.dte_emission import process_dte_emission_async

    await process_dte_emission_async(UUID(dte_id))

    # 4. Verify database state
    from app.db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        db_dte = await session.get(DTE, dte_id)
        assert db_dte is not None
        assert db_dte.status == DTEStatus.SENT
        assert db_dte.sii_track_id == "track_id_98765"
        assert db_dte.sii_xml is not None
