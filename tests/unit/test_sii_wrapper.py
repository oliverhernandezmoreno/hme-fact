from __future__ import annotations

import httpx
import pytest

from app.integrations.sii_wrapper import SIIWrapperClient, SimpleAPIClient
from tests.mocks.sii import mock_sii_upload_success, mock_simpleapi_status_success

pytestmark = [pytest.mark.unit, pytest.mark.external]


async def test_sii_wrapper_upload_uses_xml_payload() -> None:
    transport = httpx.MockTransport(mock_sii_upload_success)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = SIIWrapperClient(base_url="https://sii.test.local", http_client=http_client)
        result = await client.upload_dte_xml("<DTE />")

    assert result.track_id == "123456789"
    assert result.status == "RECIBIDO"


async def test_simpleapi_status_client_returns_status_payload() -> None:
    transport = httpx.MockTransport(mock_simpleapi_status_success)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = SimpleAPIClient(base_url="https://simpleapi.test.local", http_client=http_client)
        result = await client.get_dte_status("123456789")

    assert result["track_id"] == "123456789"
    assert result["estado"] == "ACEPTADO"
