from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

pytestmark = [pytest.mark.integration, pytest.mark.auth]


async def test_sii_status_unauthenticated(client: AsyncClient) -> None:
    # Access without auth headers
    response = await client.get("/api/v1/admin/sii/status")
    assert response.status_code == 401


async def test_sii_status_forbidden_for_regular_user(
    client: AsyncClient, auth_headers: dict
) -> None:
    # Regular user is not superadmin
    with patch(
        "app.modules.rbac.services.rbac_service.RBACService.is_super_admin", new_callable=AsyncMock
    ) as mock_check:
        mock_check.return_value = False
        response = await client.get("/api/v1/admin/sii/status", headers=auth_headers)
        assert response.status_code == 403
        assert response.json()["detail"] == "SuperAdmin access required"


async def test_sii_status_success_for_superadmin(client: AsyncClient, auth_headers: dict) -> None:
    # Superadmin user
    with (
        patch(
            "app.modules.rbac.services.rbac_service.RBACService.is_super_admin",
            new_callable=AsyncMock,
        ) as mock_check,
        patch("app.services.sii.circuit_breaker.redis.from_url") as mock_redis_class,
    ):
        mock_check.return_value = True

        # Mock Redis return values
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = lambda key: {
            "sii:cb:state": "CLOSED",
            "sii:cb:failures": "0",
            "sii:cb:last_state_change": None,
        }.get(key)
        mock_redis_class.return_value = mock_redis

        response = await client.get("/api/v1/admin/sii/status", headers=auth_headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["state"] == "CLOSED"
        assert payload["failures"] == 0
        assert payload["failure_threshold"] == 5
        assert payload["recovery_timeout_seconds"] == 60


async def test_sii_reset_success_for_superadmin(client: AsyncClient, auth_headers: dict) -> None:
    # Superadmin user resets CB
    with (
        patch(
            "app.modules.rbac.services.rbac_service.RBACService.is_super_admin",
            new_callable=AsyncMock,
        ) as mock_check,
        patch("app.services.sii.circuit_breaker.redis.from_url") as mock_redis_class,
    ):
        mock_check.return_value = True

        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = lambda key: {
            "sii:cb:state": "CLOSED",
            "sii:cb:failures": "0",
            "sii:cb:last_state_change": None,
        }.get(key)
        mock_redis_class.return_value = mock_redis

        response = await client.post("/api/v1/admin/sii/reset", headers=auth_headers)
        assert response.status_code == 200
        payload = response.json()
        assert "manually reset to CLOSED" in payload["message"]
        assert payload["status"]["state"] == "CLOSED"

        # Verify redis.set / delete called
        mock_redis.set.assert_any_call("sii:cb:state", "CLOSED")
        mock_redis.set.assert_any_call("sii:cb:failures", 0)
        mock_redis.delete.assert_called_with("sii:cb:last_state_change")


async def test_sii_simulate_failure_success(client: AsyncClient, auth_headers: dict) -> None:
    with (
        patch(
            "app.modules.rbac.services.rbac_service.RBACService.is_super_admin",
            new_callable=AsyncMock,
        ) as mock_check,
        patch("app.api.v1.endpoints.sii_admin.redis.from_url") as mock_redis_class,
    ):
        mock_check.return_value = True
        mock_redis = AsyncMock()
        mock_redis_class.return_value = mock_redis

        response = await client.post("/api/v1/admin/sii/simulate-failure", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "SII failure simulation enabled successfully"
        mock_redis.set.assert_called_once_with("sii:cb:simulate_failure", "true")


async def test_sii_clear_failure_simulation_success(
    client: AsyncClient, auth_headers: dict
) -> None:
    with (
        patch(
            "app.modules.rbac.services.rbac_service.RBACService.is_super_admin",
            new_callable=AsyncMock,
        ) as mock_check,
        patch("app.api.v1.endpoints.sii_admin.redis.from_url") as mock_redis_class,
    ):
        mock_check.return_value = True
        mock_redis = AsyncMock()
        mock_redis_class.return_value = mock_redis

        response = await client.post(
            "/api/v1/admin/sii/clear-failure-simulation", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "SII failure simulation disabled successfully"
        mock_redis.delete.assert_called_once_with("sii:cb:simulate_failure")
