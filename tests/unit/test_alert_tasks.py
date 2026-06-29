from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import ANY, AsyncMock, MagicMock, patch
from uuid import uuid4

from app.workers.tasks.alert_tasks import check_depleted_cafs_task, check_expiring_certificates_task


@patch("app.db.session.AsyncSessionLocal")
@patch("app.modules.notifications.services.email_service.EmailService")
@patch("app.workers.integration_worker.send_outbound_webhook")
def test_check_expiring_certificates(
    mock_send_outbound_webhook, mock_email_service_class, mock_session_maker
):
    mock_session = AsyncMock()
    mock_session_maker.return_value.__aenter__.return_value = mock_session

    mock_email_service = mock_email_service_class.return_value

    now = datetime.now(UTC)
    cert_a = MagicMock()
    cert_a.id = uuid4()
    cert_a.company_id = uuid4()
    cert_a.common_name = "Cert A"
    cert_a.serial_number = "12345"
    cert_a.valid_until = now + timedelta(days=10)

    mock_sub = MagicMock()
    mock_sub.id = uuid4()
    mock_sub.event_types = ["certificate.expiring"]
    mock_sub.is_active = True

    async def mock_execute(stmt, *args, **kwargs):
        stmt_str = str(stmt).lower()
        mock_res = MagicMock()
        if "certificates" in stmt_str:
            mock_res.scalars().all.return_value = [cert_a]
        elif "users" in stmt_str or "company_users" in stmt_str:
            mock_res.fetchall.return_value = [("admin@company.com",)]
        elif "webhook_subscriptions" in stmt_str:
            mock_res.scalars().all.return_value = [mock_sub]
        return mock_res

    mock_session.execute = mock_execute

    result = check_expiring_certificates_task()

    assert result == {"alerts_triggered": 1}
    mock_email_service.send_simple_email.assert_called_once_with("admin@company.com", ANY, ANY)
    mock_send_outbound_webhook.delay.assert_called_once()


@patch("app.db.session.AsyncSessionLocal")
@patch("app.modules.notifications.services.email_service.EmailService")
@patch("app.workers.integration_worker.send_outbound_webhook")
def test_check_depleted_cafs(
    mock_send_outbound_webhook, mock_email_service_class, mock_session_maker
):
    mock_session = AsyncMock()
    mock_session_maker.return_value.__aenter__.return_value = mock_session

    mock_email_service = mock_email_service_class.return_value

    caf_a = MagicMock()
    caf_a.id = uuid4()
    caf_a.company_id = uuid4()
    caf_a.dte_type = 33
    caf_a.folio_from = 100
    caf_a.folio_to = 200
    caf_a.current_folio = 185

    mock_sub = MagicMock()
    mock_sub.id = uuid4()
    mock_sub.event_types = ["caf.depleted"]

    async def mock_execute(stmt, *args, **kwargs):
        stmt_str = str(stmt).lower()
        mock_res = MagicMock()
        if "caf_files" in stmt_str:
            mock_res.scalars().all.return_value = [caf_a]
        elif "users" in stmt_str or "company_users" in stmt_str:
            mock_res.fetchall.return_value = [("admin@company.com",)]
        elif "webhook_subscriptions" in stmt_str:
            mock_res.scalars().all.return_value = [mock_sub]
        return mock_res

    mock_session.execute = mock_execute

    result = check_depleted_cafs_task()

    assert result == {"alerts_triggered": 1}
    mock_email_service.send_simple_email.assert_called_once_with("admin@company.com", ANY, ANY)
    mock_send_outbound_webhook.delay.assert_called_once()
