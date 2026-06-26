import pytest
import time
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.sii.circuit_breaker import SIICircuitBreaker, SIICircuitBreakerOpenException
from app.services.sii.client import SIIWebServicesClient


class MockRedis:
    def __init__(self):
        self.store = {}
        self.aclose = AsyncMock()

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ex=None):
        self.store[key] = str(value)
        return True

    async def incr(self, key):
        val = int(self.store.get(key, 0)) + 1
        self.store[key] = str(val)
        return val


@pytest.mark.asyncio
async def test_circuit_breaker_closed_success():
    cb = SIICircuitBreaker(failure_threshold=2, recovery_timeout=5)
    mock_redis = MockRedis()

    async def dummy_call():
        return "success"

    with patch.object(cb, "_get_redis", return_value=mock_redis):
        res = await cb.call(dummy_call)
        assert res == "success"
        assert await cb.get_state() == "CLOSED"


@pytest.mark.asyncio
async def test_circuit_breaker_tripping_on_failures():
    cb = SIICircuitBreaker(failure_threshold=2, recovery_timeout=5)
    mock_redis = MockRedis()

    async def dummy_fail():
        # Raise HTTPStatusError with status code 500
        request = httpx.Request("POST", "https://test")
        response = httpx.Response(500, request=request)
        raise httpx.HTTPStatusError("500 Internal Server Error", request=request, response=response)

    with patch.object(cb, "_get_redis", return_value=mock_redis):
        # First failure
        with pytest.raises(httpx.HTTPStatusError):
            await cb.call(dummy_fail)
        assert await cb.get_state() == "CLOSED"
        assert int(mock_redis.store.get("sii:cb:failures")) == 1

        # Second failure (should trip breaker)
        with pytest.raises(httpx.HTTPStatusError):
            await cb.call(dummy_fail)
        assert await cb.get_state() == "OPEN"

        # Third call should raise SIICircuitBreakerOpenException directly without executing
        with pytest.raises(SIICircuitBreakerOpenException):
            await cb.call(dummy_fail)


@pytest.mark.asyncio
async def test_circuit_breaker_recovery_half_open_to_closed():
    cb = SIICircuitBreaker(failure_threshold=2, recovery_timeout=1)
    mock_redis = MockRedis()

    async def dummy_fail():
        request = httpx.Request("POST", "https://test")
        response = httpx.Response(500, request=request)
        raise httpx.HTTPStatusError("500 Internal Server Error", request=request, response=response)

    async def dummy_success():
        return "ok"

    with patch.object(cb, "_get_redis", return_value=mock_redis):
        # Trip the breaker
        with pytest.raises(httpx.HTTPStatusError):
            await cb.call(dummy_fail)
        with pytest.raises(httpx.HTTPStatusError):
            await cb.call(dummy_fail)
        assert await cb.get_state() == "OPEN"

        # Wait for recovery timeout to pass
        time.sleep(1.1)

        # State should automatically evaluate to HALF_OPEN
        assert await cb.get_state() == "HALF_OPEN"

        # A successful call in HALF_OPEN should close the breaker and reset failures
        res = await cb.call(dummy_success)
        assert res == "ok"
        assert await cb.get_state() == "CLOSED"
        assert int(mock_redis.store.get("sii:cb:failures")) == 0


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_failure_reopens():
    cb = SIICircuitBreaker(failure_threshold=2, recovery_timeout=1)
    mock_redis = MockRedis()

    async def dummy_fail():
        request = httpx.Request("POST", "https://test")
        response = httpx.Response(500, request=request)
        raise httpx.HTTPStatusError("500 Internal Server Error", request=request, response=response)

    with patch.object(cb, "_get_redis", return_value=mock_redis):
        # Trip the breaker
        with pytest.raises(httpx.HTTPStatusError):
            await cb.call(dummy_fail)
        with pytest.raises(httpx.HTTPStatusError):
            await cb.call(dummy_fail)
        assert await cb.get_state() == "OPEN"

        # Wait for recovery timeout to pass
        time.sleep(1.1)
        assert await cb.get_state() == "HALF_OPEN"

        # A failure in HALF_OPEN should immediately reopen the breaker
        with pytest.raises(httpx.HTTPStatusError):
            await cb.call(dummy_fail)
        assert await cb.get_state() == "OPEN"


@pytest.mark.asyncio
async def test_sii_client_integration_with_circuit_breaker():
    client = SIIWebServicesClient(environment="certification")
    # Trip the breaker manually on client
    client.circuit_breaker.get_state = AsyncMock(return_value="OPEN")

    with pytest.raises(SIICircuitBreakerOpenException):
        await client.get_seed()


def test_circuit_breaker_settings_defaults():
    cb = SIICircuitBreaker()
    assert cb.failure_threshold == 5
    assert cb.recovery_timeout == 60

