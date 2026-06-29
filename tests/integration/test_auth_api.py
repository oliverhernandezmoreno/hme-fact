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


async def test_login_sets_cookie(client: AsyncClient, user) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "ChangeMe123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies


async def test_cookie_authentication(client: AsyncClient, user) -> None:
    # Login to set the cookie in the client session
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "ChangeMe123!"},
    )
    assert login_response.status_code == 200

    # Access protected endpoint (without Authorization header)
    protected_response = await client.get("/api/v1/companies")
    assert protected_response.status_code == 200


async def test_logout_clears_cookie(client: AsyncClient, user) -> None:
    # Login
    await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "ChangeMe123!"},
    )
    assert "access_token" in client.cookies

    # Logout
    logout_response = await client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200

    # Cookie is deleted/expired
    assert client.cookies.get("access_token") is None
