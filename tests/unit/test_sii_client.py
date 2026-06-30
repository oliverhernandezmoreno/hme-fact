import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.sii.client import SIIWebServicesClient


@pytest.mark.asyncio
async def test_get_token_hits_cache_and_avoids_sii_call():
    # Setup
    pfx_data = b"my_fake_pfx_data"
    pfx_password = "password"
    pfx_hash = hashlib.sha256(pfx_data).hexdigest()
    token_key = f"sii:token:{pfx_hash}"

    mock_redis = AsyncMock()
    mock_redis.get.return_value = "CACHED_TOKEN_123"

    client = SIIWebServicesClient(environment="certification")

    # Mock redis.from_url and _fetch_token_from_sii
    with (
        patch("redis.asyncio.from_url", return_value=mock_redis),
        patch.object(client, "_fetch_token_from_sii", new_callable=AsyncMock) as mock_fetch,
    ):
        token = await client.get_token(pfx_data, pfx_password)

        assert token == "CACHED_TOKEN_123"
        mock_redis.get.assert_called_once_with(token_key)
        mock_fetch.assert_not_called()
        mock_redis.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_get_token_misses_cache_calls_sii_and_caches_result():
    pfx_data = b"my_fake_pfx_data"
    pfx_password = "password"
    pfx_hash = hashlib.sha256(pfx_data).hexdigest()
    token_key = f"sii:token:{pfx_hash}"
    lock_key = f"lock:sii:token:{pfx_hash}"

    mock_redis = AsyncMock()
    # Cache miss
    mock_redis.get.return_value = None

    # Mock Redis Lock as async context manager
    mock_lock = MagicMock()
    mock_lock.__aenter__ = AsyncMock(return_value=mock_lock)
    mock_lock.__aexit__ = AsyncMock(return_value=None)
    mock_redis.lock = MagicMock(return_value=mock_lock)

    client = SIIWebServicesClient(environment="certification")

    with (
        patch("redis.asyncio.from_url", return_value=mock_redis),
        patch.object(
            client, "_fetch_token_from_sii", AsyncMock(return_value="NEW_TOKEN_999")
        ) as mock_fetch,
    ):
        token = await client.get_token(pfx_data, pfx_password)

        assert token == "NEW_TOKEN_999"
        mock_redis.lock.assert_called_once_with(lock_key, timeout=30, sleep=0.1)
        mock_fetch.assert_called_once_with(pfx_data, pfx_password)
        mock_redis.set.assert_called_once_with(token_key, "NEW_TOKEN_999", ex=6300)
        mock_redis.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_get_token_redis_error_falls_back_to_direct_sii_call():
    pfx_data = b"my_fake_pfx_data"
    pfx_password = "password"

    client = SIIWebServicesClient(environment="certification")

    # redis.from_url raises an exception to simulate Redis service failure
    with (
        patch("redis.asyncio.from_url", side_effect=Exception("Redis connection error")),
        patch.object(
            client, "_fetch_token_from_sii", AsyncMock(return_value="DIRECT_TOKEN_555")
        ) as mock_fetch,
    ):
        token = await client.get_token(pfx_data, pfx_password)

        assert token == "DIRECT_TOKEN_555"
        mock_fetch.assert_called_once_with(pfx_data, pfx_password)


@pytest.mark.asyncio
async def test_get_seed_success():
    client = SIIWebServicesClient(environment="certification")

    # Mock SOAP response for getSeed
    soap_resp = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soapenv:Body>
      <getSeedReturn>&lt;SII:RESPUESTA xmlns:SII="http://www.sii.cl/XMLSchema"&gt;&lt;SII:RESP_BODY&gt;&lt;SEMILLA&gt;123456789012&lt;/SEMILLA&gt;&lt;/SII:RESP_BODY&gt;&lt;/SII:RESPUESTA&gt;</getSeedReturn>
   </soapenv:Body>
</soapenv:Envelope>"""

    # Mock client.circuit_breaker.call to return response content directly
    # to avoid HTTP network call
    async def mock_cb_call(func, *args, **kwargs):
        return soap_resp.encode("utf-8")

    client.circuit_breaker.call = mock_cb_call

    seed = await client.get_seed()
    assert seed == "123456789012"


@pytest.mark.asyncio
async def test_enviar_dte_success():
    client = SIIWebServicesClient(environment="certification")

    # Mock UPL response
    upl_resp = """<?xml version="1.0" encoding="UTF-8"?>
<RECEPCIONDTE>
    <STATUS>0</STATUS>
    <TRACKID>987654321</TRACKID>
</RECEPCIONDTE>"""

    async def mock_cb_call(func, *args, **kwargs):
        return upl_resp.encode("utf-8")

    client.circuit_breaker.call = mock_cb_call

    track_id = await client.enviar_dte(b"<xml/>", "TOKEN", "1-9", "2-7")
    assert track_id == "987654321"


@pytest.mark.asyncio
async def test_enviar_dte_error_status():
    client = SIIWebServicesClient(environment="certification")

    # Mock UPL response with failure status
    upl_resp = """<?xml version="1.0" encoding="UTF-8"?>
<RECEPCIONDTE>
    <STATUS>1</STATUS>
</RECEPCIONDTE>"""

    async def mock_cb_call(func, *args, **kwargs):
        return upl_resp.encode("utf-8")

    client.circuit_breaker.call = mock_cb_call

    with pytest.raises(ValueError, match="El SII rechazó el envío. Status: 1"):
        await client.enviar_dte(b"<xml/>", "TOKEN", "1-9", "2-7")


@pytest.mark.asyncio
async def test_simulate_failure_via_settings():
    client = SIIWebServicesClient(environment="certification")
    client.settings.SII_SIMULATE_FAILURE = True

    import httpx

    with pytest.raises(httpx.HTTPStatusError, match="Simulated SII 500"):
        await client.get_seed()


@pytest.mark.asyncio
async def test_simulate_failure_via_redis():
    client = SIIWebServicesClient(environment="certification")
    client.settings.SII_SIMULATE_FAILURE = False

    mock_redis = AsyncMock()
    mock_redis.get.return_value = "true"

    import httpx

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        with pytest.raises(httpx.HTTPStatusError, match="Simulated SII 500"):
            await client.get_seed()
