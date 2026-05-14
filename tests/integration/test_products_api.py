from __future__ import annotations

from decimal import Decimal

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


async def test_product_crud_flow(
    client: AsyncClient,
    tenant_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/products",
        headers=tenant_headers,
        json={
            "sku": "TEST-001",
            "name": "Servicio Testing",
            "description": "Servicio cubierto por tests",
            "unit": "UN",
            "unit_price": str(Decimal("15000.00")),
            "tax_exempt": False,
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    get_response = await client.get(f"/api/v1/products/{product_id}", headers=tenant_headers)
    assert get_response.status_code == 200
    assert get_response.json()["sku"] == "TEST-001"

    update_response = await client.patch(
        f"/api/v1/products/{product_id}",
        headers=tenant_headers,
        json={"name": "Servicio Testing Actualizado"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Servicio Testing Actualizado"
