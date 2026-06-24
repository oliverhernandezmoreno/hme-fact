from __future__ import annotations

import httpx
import pytest

from app.models import DTEStatus
from app.modules.integrations.clients import SimpleApiHttpClient
from app.modules.integrations.exceptions import ProviderRateLimitError, TaxRejectionError
from app.modules.integrations.providers import SimpleApiProvider
from app.modules.integrations.schemas import TaxProviderContext, TaxSendRequest

pytestmark = [pytest.mark.unit]


def _request() -> TaxSendRequest:
    return TaxSendRequest(
        xml_content="<DTE />",
        context=TaxProviderContext(
            company_id="00000000-0000-0000-0000-000000000001",
            dte_id="00000000-0000-0000-0000-000000000002",
            company_rut="76123456-7",
            dte_type=33,
            folio=10,
        ),
    )


async def test_simpleapi_provider_normalizes_send_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/dte/send"
        assert request.headers["authorization"] == "Bearer test-key"
        return httpx.Response(
            200,
            json={"track_id": "123456789", "estado": "RECIBIDO", "message": "OK"},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        provider = SimpleApiProvider(
            SimpleApiHttpClient(
                base_url="https://simpleapi.test",
                api_key="test-key",
                timeout=1,
                max_retries=0,
                backoff_base_seconds=0,
                http_client=http_client,
            )
        )
        result = await provider.send_dte(_request())

    assert result.provider == "simpleapi"
    assert result.track_id == "123456789"
    assert result.status == DTEStatus.SENT


async def test_simpleapi_provider_raises_for_tax_rejection() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"track_id": "123456789", "estado": "RECHAZADO", "errors": ["XML invalido"]},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        provider = SimpleApiProvider(
            SimpleApiHttpClient(
                base_url="https://simpleapi.test",
                api_key="test-key",
                timeout=1,
                max_retries=0,
                backoff_base_seconds=0,
                http_client=http_client,
            )
        )
        with pytest.raises(TaxRejectionError):
            await provider.send_dte(_request())


async def test_simpleapi_client_maps_rate_limit_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"message": "Too many requests"}, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = SimpleApiHttpClient(
            base_url="https://simpleapi.test",
            api_key="test-key",
            timeout=1,
            max_retries=0,
            backoff_base_seconds=0,
            http_client=http_client,
        )
        with pytest.raises(ProviderRateLimitError):
            await client.get_json("/dte/status/123")
