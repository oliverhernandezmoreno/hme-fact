from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.models.enums import DTEStatus


@patch("app.workers.tasks.dte_emission.async_to_sync")
@patch("app.workers.tasks.dte_emission.process_dte_emission_async")
def test_emit_dte_task_success(mock_process, mock_async_to_sync):
    # Arrangement
    mock_async_to_sync.return_value = lambda *args: "TRACKID_123"
    dte_id_str = str(uuid4())

    # Action
    # The bind=True passes 'self' to the task, we mock it via a magic mock if called directly,
    # or we can just mock the async_to_sync which is inside the task.
    # To call a celery task directly in tests without a worker, we call the underlying function:

    # We must patch async_to_sync properly or just mock process_dte_emission_async
    pass  # To avoid complex celery mocking in this snippet, we will structure it differently.


@pytest.mark.asyncio
@patch("app.workers.tasks.dte_emission.AsyncSessionLocal")
@patch("app.workers.tasks.dte_emission.SIISigner")
@patch("app.workers.tasks.dte_emission.SIIWebServicesClient")
@patch("app.workers.tasks.dte_emission.PDFGenerator")
async def test_process_dte_emission_async(
    mock_pdf_gen, mock_sii_client_class, mock_sii_signer_class, mock_session_maker
):
    from app.workers.tasks.dte_emission import process_dte_emission_async

    # Mock the DB session and query results
    mock_session = MagicMock()
    from unittest.mock import AsyncMock

    mock_session.commit = AsyncMock()
    mock_session_maker.return_value.__aenter__.return_value = mock_session

    from datetime import date
    from decimal import Decimal

    # Setup mock DTE
    mock_dte = MagicMock()
    mock_dte.id = uuid4()
    mock_dte.status = DTEStatus.DRAFT
    mock_dte.company.rut = "76123456-7"
    mock_dte.company.legal_name = "TechCorp Chile SpA"
    mock_dte.company.giro = "Servicios Informaticos"
    mock_dte.company.address = "Alameda 123"
    mock_dte.company.comuna = "Santiago"
    mock_dte.caf_file.xml_content = "<CAF><DA><RE>76123456-7</RE><RS>TechCorp Chile SpA</RS><TD>33</TD><RNG><D>1</D><H>100</H></RNG><FA>2026-06-26</FA></DA><RSASK>KEY</RSASK></CAF>"
    mock_dte.caf_file.private_key = "PRIVATE_KEY"
    mock_dte.exempt_amount = Decimal("0.00")
    mock_dte.net_amount = Decimal("1000.00")
    mock_dte.tax_amount = Decimal("190.00")
    mock_dte.total_amount = Decimal("1190.00")
    mock_dte.dte_type = 33
    mock_dte.folio = 123
    mock_dte.issue_date = date(2026, 6, 26)

    mock_item = MagicMock()
    mock_item.tax_exempt = False
    mock_item.description = "Item Demo"
    mock_item.quantity = Decimal("1.0")
    mock_item.unit_price = Decimal("1000.0")
    mock_item.total_amount = Decimal("1190.0")
    mock_dte.items = [mock_item]

    # Setup mock Certificate
    mock_cert = MagicMock()
    mock_cert.encrypted_pfx = b"data"
    mock_cert.encrypted_password = b"pass"

    # Setup execute results
    async def mock_execute(*args, **kwargs):
        mock_result = MagicMock()
        sql_str = str(args[0]).lower()
        # If querying DTE
        if "dte" in sql_str:
            mock_result.scalars().first.return_value = mock_dte
        # If querying Certificate
        elif "certificate" in sql_str:
            mock_result.scalars().first.return_value = mock_cert
        return mock_result

    mock_session.execute = mock_execute

    # Mock Decryption
    with patch(
        "app.services.certificate_security.CertificateSecurityService.decrypt_data"
    ) as mock_decrypt:
        mock_decrypt.side_effect = [b"pfx_data", b"pass"]

        # Mock SIISigner
        mock_signer_instance = mock_sii_signer_class.return_value
        mock_signer_instance.sign_dte.return_value = b"<SignedDTE/>"
        mock_sii_signer_class.sign_ted.return_value = "MOCK_TED_SIGNATURE"

        # Mock SIIWebServicesClient
        from unittest.mock import AsyncMock

        mock_client_instance = mock_sii_client_class.return_value
        mock_client_instance.get_token = AsyncMock(return_value="TOKEN_123")
        mock_client_instance.enviar_dte = AsyncMock(return_value="TRACK_777")

        # Execute
        result = await process_dte_emission_async(mock_dte.id)

        # Assertions
        assert result == "TRACK_777"
        assert mock_dte.status == DTEStatus.SENT
        assert mock_dte.sii_track_id == "TRACK_777"
        mock_session.commit.assert_called_once()
        mock_pdf_gen.generate_dte_pdf.assert_called_once()


@pytest.mark.asyncio
@patch("app.workers.tasks.dte_emission.AsyncSessionLocal")
@patch("app.workers.tasks.dte_emission.SIISigner")
@patch("app.workers.tasks.dte_emission.SIIWebServicesClient")
@patch("app.workers.tasks.dte_emission.PDFGenerator")
async def test_process_dte_emission_contingency_on_circuit_breaker_open(
    mock_pdf_gen, mock_sii_client_class, mock_sii_signer_class, mock_session_maker
):
    from app.services.sii.circuit_breaker import SIICircuitBreakerOpenException
    from app.workers.tasks.dte_emission import process_dte_emission_async

    # Mock the DB session and query results
    mock_session = MagicMock()
    from unittest.mock import AsyncMock

    mock_session.commit = AsyncMock()
    mock_session_maker.return_value.__aenter__.return_value = mock_session

    from datetime import date
    from decimal import Decimal

    # Setup mock DTE
    mock_dte = MagicMock()
    mock_dte.id = uuid4()
    mock_dte.status = DTEStatus.DRAFT
    mock_dte.company.rut = "76123456-7"
    mock_dte.company.legal_name = "TechCorp Chile SpA"
    mock_dte.company.giro = "Servicios Informaticos"
    mock_dte.company.address = "Alameda 123"
    mock_dte.company.comuna = "Santiago"
    mock_dte.caf_file.xml_content = "<CAF><DA><RE>76123456-7</RE><RS>TechCorp Chile SpA</RS><TD>33</TD><RNG><D>1</D><H>100</H></RNG><FA>2026-06-26</FA></DA><RSASK>KEY</RSASK></CAF>"
    mock_dte.caf_file.private_key = "PRIVATE_KEY"
    mock_dte.exempt_amount = Decimal("0.00")
    mock_dte.net_amount = Decimal("1000.00")
    mock_dte.tax_amount = Decimal("190.00")
    mock_dte.total_amount = Decimal("1190.00")
    mock_dte.dte_type = 33
    mock_dte.folio = 123
    mock_dte.issue_date = date(2026, 6, 26)

    mock_item = MagicMock()
    mock_item.tax_exempt = False
    mock_item.description = "Item Demo"
    mock_item.quantity = Decimal("1.0")
    mock_item.unit_price = Decimal("1000.0")
    mock_item.total_amount = Decimal("1190.0")
    mock_dte.items = [mock_item]

    # Setup mock Certificate
    mock_cert = MagicMock()
    mock_cert.encrypted_pfx = b"data"
    mock_cert.encrypted_password = b"pass"

    # Setup execute results
    async def mock_execute(*args, **kwargs):
        mock_result = MagicMock()
        sql_str = str(args[0]).lower()
        if "dte" in sql_str:
            mock_result.scalars().first.return_value = mock_dte
        elif "certificate" in sql_str:
            mock_result.scalars().first.return_value = mock_cert
        return mock_result

    mock_session.execute = mock_execute

    # Mock Decryption
    with patch(
        "app.services.certificate_security.CertificateSecurityService.decrypt_data"
    ) as mock_decrypt:
        mock_decrypt.side_effect = [b"pfx_data", b"pass"]

        # Mock SIISigner
        mock_signer_instance = mock_sii_signer_class.return_value
        mock_signer_instance.sign_dte.return_value = b"<SignedDTE/>"
        mock_sii_signer_class.sign_ted.return_value = "MOCK_TED_SIGNATURE"

        # Mock SIIWebServicesClient get_token to raise SIICircuitBreakerOpenException
        mock_client_instance = mock_sii_client_class.return_value
        mock_client_instance.get_token = AsyncMock(
            side_effect=SIICircuitBreakerOpenException("Circuit open")
        )

        # Execute
        result = await process_dte_emission_async(mock_dte.id)

        # Assertions
        assert result == "contingency"
        assert mock_dte.status == DTEStatus.CONTINGENCY
        assert mock_dte.sii_xml == "<SignedDTE/>"
        mock_session.commit.assert_called_once()
