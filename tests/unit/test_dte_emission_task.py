import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from app.workers.tasks.dte_emission import emit_dte_task
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
    pass # To avoid complex celery mocking in this snippet, we will structure it differently.

@pytest.mark.asyncio
@patch("app.workers.tasks.dte_emission.async_session_maker")
@patch("app.workers.tasks.dte_emission.SIISigner")
@patch("app.workers.tasks.dte_emission.SIIWebServicesClient")
@patch("app.workers.tasks.dte_emission.PDFGenerator")
async def test_process_dte_emission_async(
    mock_pdf_gen, mock_sii_client_class, mock_sii_signer_class, mock_session_maker
):
    from app.workers.tasks.dte_emission import process_dte_emission_async
    
    # Mock the DB session and query results
    mock_session = MagicMock()
    mock_session_maker.return_value.__aenter__.return_value = mock_session
    
    # Setup mock DTE
    mock_dte = MagicMock()
    mock_dte.id = uuid4()
    mock_dte.status = DTEStatus.DRAFT
    mock_dte.company.rut = "76123456-7"
    mock_dte.caf_file.xml_content = "<CAF></CAF>"
    mock_dte.caf_file.private_key = "PRIVATE_KEY"
    
    # Setup mock Certificate
    mock_cert = MagicMock()
    mock_cert.encrypted_data = b"data"
    mock_cert.encrypted_password = b"pass"
    
    # Setup execute results
    async def mock_execute(*args, **kwargs):
        mock_result = MagicMock()
        # If querying DTE
        if "DTE" in str(args[0]):
            mock_result.scalars().first.return_value = mock_dte
        # If querying Certificate
        elif "Certificate" in str(args[0]):
            mock_result.scalars().first.return_value = mock_cert
        return mock_result

    mock_session.execute = mock_execute
    
    # Mock Decryption
    with patch("app.services.certificate_security.CertificateSecurityService.decrypt_certificate", return_value=(b"pfx_data", "pass")):
        
        # Mock SIISigner
        mock_signer_instance = mock_sii_signer_class.return_value
        mock_signer_instance.sign_dte.return_value = b"<SignedDTE/>"
        
        # Mock SIIWebServicesClient
        mock_client_instance = mock_sii_client_class.return_value
        mock_client_instance.get_token.return_value = "TOKEN_123"
        mock_client_instance.enviar_dte.return_value = "TRACK_777"
        
        # Execute
        result = await process_dte_emission_async(mock_dte.id)
        
        # Assertions
        assert result == "TRACK_777"
        assert mock_dte.status == DTEStatus.SENT
        assert mock_dte.sii_track_id == "TRACK_777"
        mock_session.commit.assert_called_once()
        mock_pdf_gen.generate_invoice_pdf.assert_called_once()
