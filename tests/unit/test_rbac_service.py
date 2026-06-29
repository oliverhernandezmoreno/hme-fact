"""Unit tests for RBACService."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.rbac.services.rbac_service import SYSTEM_ROLES, RBACService


@pytest.fixture
def user_id():
    return uuid.uuid4()


@pytest.fixture
def company_id():
    return uuid.uuid4()


@pytest.fixture
def mock_session():
    return AsyncMock()


class TestRBACService:
    def test_system_roles_defined(self):
        """All 6 system roles must be defined."""
        expected = {"SuperAdmin", "CompanyOwner", "Accountant", "Seller", "Viewer", "APIUser"}
        assert set(SYSTEM_ROLES.keys()) == expected

    def test_super_admin_scope_is_platform(self):
        assert SYSTEM_ROLES["SuperAdmin"]["scope"] == "platform"

    def test_company_roles_scope(self):
        company_roles = ["CompanyOwner", "Accountant", "Seller", "Viewer", "APIUser"]
        for role in company_roles:
            assert SYSTEM_ROLES[role]["scope"] == "company"

    @pytest.mark.asyncio
    async def test_is_super_admin_true(self, mock_session, user_id):
        svc = RBACService(mock_session)
        with patch.object(svc._user_role_repo, "has_role", return_value=True):
            result = await svc.is_super_admin(user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_super_admin_false(self, mock_session, user_id):
        svc = RBACService(mock_session)
        with patch.object(svc._user_role_repo, "has_role", return_value=False):
            result = await svc.is_super_admin(user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_has_permission_super_admin_bypasses(self, mock_session, user_id, company_id):
        """SuperAdmin should always have permission."""
        svc = RBACService(mock_session)
        with patch.object(svc._user_role_repo, "has_role", return_value=True):
            result = await svc.has_permission(user_id, company_id, "any_module", "any_action")
        assert result is True

    @pytest.mark.asyncio
    async def test_has_permission_wildcard(self, mock_session, user_id, company_id):
        svc = RBACService(mock_session)
        with (
            patch.object(svc._user_role_repo, "has_role", return_value=False),
            patch.object(
                svc._user_role_repo, "get_user_permissions", return_value={("dte", "read", "*")}
            ),
        ):
            result = await svc.has_permission(user_id, company_id, "dte", "read")
        assert result is True

    @pytest.mark.asyncio
    async def test_assign_role_not_found(self, mock_session, user_id, company_id):
        svc = RBACService(mock_session)
        with patch.object(svc._role_repo, "get_by_name", return_value=None):
            with pytest.raises(ValueError, match="not found"):
                await svc.assign_role(user_id, "NonExistentRole", company_id)

    @pytest.mark.asyncio
    async def test_assign_role_success(self, mock_session, user_id, company_id):
        svc = RBACService(mock_session)
        mock_role = MagicMock()
        mock_role.id = uuid.uuid4()

        with (
            patch.object(svc._role_repo, "get_by_name", return_value=mock_role),
            patch.object(svc._user_role_repo, "assign_role", return_value=MagicMock()),
        ):
            await svc.assign_role(user_id, "Accountant", company_id)
            svc._user_role_repo.assign_role.assert_called_once_with(
                user_id, mock_role.id, company_id
            )
