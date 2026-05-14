from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = [pytest.mark.integration, pytest.mark.auth]


async def test_login_returns_access_token(client: AsyncClient, user) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "ChangeMe123!"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


async def test_login_rejects_invalid_password(client: AsyncClient, user) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "wrong-password"},
    )

    assert response.status_code == 401
