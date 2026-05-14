from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = [pytest.mark.integration, pytest.mark.xml]


async def test_generate_dte_xml_persists_and_returns_xml(
    client: AsyncClient,
    tenant_headers: dict[str, str],
    dte,
) -> None:
    response = await client.post(f"/api/v1/dte/{dte.id}/generate-xml", headers=tenant_headers)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "<TipoDTE>33</TipoDTE>" in response.text
    assert '<TED version="1.0">' in response.text
