"""Unit tests for APIKeyService."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
import uuid

import pytest

from app.modules.apikeys.services.api_key_service import APIKeyService, APIKeyServiceError


@pytest.fixture
def company_id():
    return uuid.uuid4()


@pytest.fixture
def user_id():
    return uuid.uuid4()


@pytest.fixture
def mock_session():
    return AsyncMock()


class TestAPIKeyService:
    @pytest.mark.asyncio
    async def test_generate_api_key(self, mock_session, company_id, user_id):
        svc = APIKeyService(mock_session)
        mock_key = MagicMock()
        mock_key.id = uuid.uuid4()
        mock_key.name = "Test Key"
        mock_key.prefix = "abcdefgh"
        mock_key.scopes = ["read", "dte"]
        mock_key.expires_at = None

        with patch.object(svc._repo, "generate_key_pair", return_value=("abcdefgh", "abcdefgh.secretvalue", "hashed")), \
             patch.object(svc._repo, "create", return_value=mock_key):
            result = await svc.generate(
                company_id=company_id,
                name="Test Key",
                created_by_user_id=user_id,
                scopes=["read", "dte"],
            )

        assert result.raw_key == "abcdefgh.secretvalue"
        assert result.api_key.name == "Test Key"

    @pytest.mark.asyncio
    async def test_generate_invalid_scope(self, mock_session, company_id, user_id):
        svc = APIKeyService(mock_session)
        with pytest.raises(APIKeyServiceError, match="Invalid scopes"):
            await svc.generate(
                company_id=company_id,
                name="Bad Key",
                created_by_user_id=user_id,
                scopes=["invalid_scope"],
            )

    @pytest.mark.asyncio
    async def test_validate_expired_key(self, mock_session):
        svc = APIKeyService(mock_session)
        expired_key = MagicMock()
        expired_key.expires_at = datetime.now(timezone.utc) - timedelta(days=1)

        with patch.object(svc._repo, "get_by_prefix_and_hash", return_value=expired_key):
            result = await svc.validate("prefix.secret")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_valid_key(self, mock_session):
        svc = APIKeyService(mock_session)
        valid_key = MagicMock()
        valid_key.id = uuid.uuid4()
        valid_key.expires_at = None

        with patch.object(svc._repo, "get_by_prefix_and_hash", return_value=valid_key), \
             patch.object(svc._repo, "touch_last_used", return_value=None):
            result = await svc.validate("prefix.secret")

        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_not_found(self, mock_session):
        svc = APIKeyService(mock_session)
        with patch.object(svc._repo, "get_by_prefix_and_hash", return_value=None):
            result = await svc.validate("bad.key")
        assert result is None

    @pytest.mark.asyncio
    async def test_revoke_wrong_company(self, mock_session, company_id):
        svc = APIKeyService(mock_session)
        other_key = MagicMock()
        other_key.company_id = uuid.uuid4()  # Different company

        with patch.object(svc._repo, "get", return_value=other_key):
            with pytest.raises(APIKeyServiceError, match="access denied"):
                await svc.revoke(uuid.uuid4(), company_id)

    @pytest.mark.asyncio
    async def test_rotate_creates_new_key(self, mock_session, company_id, user_id):
        svc = APIKeyService(mock_session)
        old_key = MagicMock()
        old_key.company_id = company_id
        old_key.name = "Old Key"
        old_key.scopes = ["read"]

        new_key = MagicMock()
        new_key.id = uuid.uuid4()
        new_key.name = "Old Key (rotated)"
        new_key.prefix = "newprefix"
        new_key.expires_at = None

        with patch.object(svc._repo, "get", return_value=old_key), \
             patch.object(svc._repo, "revoke", return_value=None), \
             patch.object(svc._repo, "generate_key_pair", return_value=("newprefix", "newprefix.newsecret", "newhash")), \
             patch.object(svc._repo, "create", return_value=new_key):
            result = await svc.rotate(old_key.id, company_id, user_id)

        assert result.raw_key == "newprefix.newsecret"
