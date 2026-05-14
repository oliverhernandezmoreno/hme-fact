from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


async def test_customer_crud_flow(
    client: AsyncClient,
    tenant_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/customers",
        headers=tenant_headers,
        json={
            "rut": "77222222-2",
            "legal_name": "Cliente API SpA",
            "giro": "Comercio",
            "email": "cliente.api@example.com",
            "phone": "+56912345678",
            "address": "Alameda 456",
            "comuna": "Santiago",
            "city": "Santiago",
        },
    )
    assert create_response.status_code == 201
    customer_id = create_response.json()["id"]

    list_response = await client.get("/api/v1/customers", headers=tenant_headers)
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == customer_id

    update_response = await client.patch(
        f"/api/v1/customers/{customer_id}",
        headers=tenant_headers,
        json={"legal_name": "Cliente API Actualizado SpA"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["legal_name"] == "Cliente API Actualizado SpA"
