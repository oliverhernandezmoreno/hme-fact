import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.services.audit import AuditLogService


@pytest.mark.asyncio
async def test_log_action():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    service = AuditLogService(mock_session)

    company_id = uuid4()
    user_id = uuid4()
    entity_id = uuid4()

    audit_log = await service.log_action(
        action="update",
        entity_type="DTE",
        entity_id=entity_id,
        company_id=company_id,
        user_id=user_id,
        previous_data={"status": "draft"},
        new_data={"status": "sent"},
        ip_address="127.0.0.1",
        user_agent="pytest",
    )

    assert audit_log.action == "update"
    assert audit_log.entity_type == "DTE"
    assert audit_log.entity_id == entity_id
    assert audit_log.company_id == company_id
    assert audit_log.user_id == user_id
    assert audit_log.previous_data == {"status": "draft"}
    assert audit_log.new_data == {"status": "sent"}
    assert audit_log.ip_address == "127.0.0.1"
    assert audit_log.user_agent == "pytest"

    mock_session.add.assert_called_once_with(audit_log)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(audit_log)
