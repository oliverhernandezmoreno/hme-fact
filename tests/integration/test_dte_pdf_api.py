from __future__ import annotations

import pytest
from httpx import AsyncClient
from app.services.storage import get_file_storage_service

pytestmark = [pytest.mark.integration]


async def test_get_dte_pdf_returns_streaming_response(
    client: AsyncClient,
    tenant_headers: dict[str, str],
    dte,
) -> None:
    # 1. Write a dummy PDF to storage
    storage = get_file_storage_service()
    path = f"companies/{dte.company_id}/dtes/{dte.id}/dte_{dte.folio}.pdf"
    await storage.save_file(path, b"%PDF-1.4 dummy pdf content")
    
    try:
        # 2. Request the PDF download
        response = await client.get(f"/api/v1/dte/{dte.id}/pdf", headers=tenant_headers)
        
        # 3. Assertions
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert f"filename=dte_{dte.folio}.pdf" in response.headers["content-disposition"]
        assert response.content == b"%PDF-1.4 dummy pdf content"
    finally:
        # Cleanup
        await storage.delete_file(path)


async def test_get_dte_pdf_not_found(
    client: AsyncClient,
    tenant_headers: dict[str, str],
    dte,
) -> None:
    # Attempt to request PDF that doesn't exist in storage
    response = await client.get(f"/api/v1/dte/{dte.id}/pdf", headers=tenant_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "PDF not generated yet"
