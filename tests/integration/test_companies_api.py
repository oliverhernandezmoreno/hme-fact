from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


async def test_create_company_associates_current_user(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/api/v1/companies",
        headers=auth_headers,
        json={
            "rut": "76111111-1",
            "legal_name": "Nueva Empresa SpA",
            "fantasy_name": "Nueva Empresa",
            "giro": "Servicios",
            "address": "Av Test 123",
            "comuna": "Santiago",
            "city": "Santiago",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["rut"] == "76111111-1"
    assert payload["legal_name"] == "Nueva Empresa SpA"


async def test_list_companies_returns_only_user_companies(
    client: AsyncClient,
    auth_headers: dict[str, str],
    company,
) -> None:
    response = await client.get("/api/v1/companies", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == str(company.id)
