import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import FastAPI, Request
from httpx import AsyncClient, ASGITransport
from app.core.middleware.idempotency_middleware import IdempotencyMiddleware

@pytest.fixture
def dummy_app():
    app = FastAPI()
    
    # Simple endpoint that increments a counter to verify execution
    counter = {"count": 0}
    
    @app.post("/public/resource")
    async def post_resource(request: Request):
        counter["count"] += 1
        return {"count": counter["count"], "msg": "created"}
        
    app.add_middleware(IdempotencyMiddleware)
    return app

@pytest.mark.asyncio
async def test_idempotency_first_request_and_subsequent_hit(dummy_app):
    mock_redis = AsyncMock()
    # First call: set NX returns True (not exists)
    mock_redis.set.side_effect = [True, True] # First for NX check, second for saving cache
    mock_redis.get.return_value = None
    
    # Setup mock data for subsequent call (cache hit)
    cached_response = {
        "status_code": 200,
        "content": '{"count": 1, "msg": "created"}',
        "headers": {"content-type": "application/json"}
    }
    
    async with AsyncClient(transport=ASGITransport(app=dummy_app), base_url="http://test") as client:
        # Patch Redis connection
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            # 1. First Request (Cache Miss)
            response1 = await client.post(
                "/public/resource",
                headers={"idempotency-key": "unique-key-123"}
            )
            assert response1.status_code == 200
            assert response1.json() == {"count": 1, "msg": "created"}
            assert response1.headers.get("X-Cache-Idempotency") == "MISS"
            
            # Verify it set the processing flag
            mock_redis.set.assert_any_call("idempotency:global:unique-key-123", "processing", nx=True, ex=30)
            
            # 2. Second Request (Cache Hit)
            # Configure mock to return False for NX set (already exists)
            mock_redis.set.side_effect = None
            mock_redis.set.return_value = False
            mock_redis.get.return_value = json.dumps(cached_response)
            
            response2 = await client.post(
                "/public/resource",
                headers={"idempotency-key": "unique-key-123"}
            )
            assert response2.status_code == 200
            assert response2.json() == {"count": 1, "msg": "created"}
            assert response2.headers.get("X-Cache-Idempotency") == "HIT"

@pytest.mark.asyncio
async def test_idempotency_concurrent_request_conflict(dummy_app):
    mock_redis = AsyncMock()
    # NX set returns False (key exists)
    mock_redis.set.return_value = False
    # Value is "processing" indicating concurrent request is active
    mock_redis.get.return_value = "processing"
    
    async with AsyncClient(transport=ASGITransport(app=dummy_app), base_url="http://test") as client:
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            response = await client.post(
                "/public/resource",
                headers={"idempotency-key": "concurrent-key"}
            )
            assert response.status_code == 409
            assert response.json()["error"] == "conflict"
            assert "already in progress" in response.json()["message"]

@pytest.mark.asyncio
async def test_idempotency_fail_open_on_redis_error(dummy_app):
    async with AsyncClient(transport=ASGITransport(app=dummy_app), base_url="http://test") as client:
        # Simulate Redis connection error
        with patch("redis.asyncio.from_url", side_effect=Exception("Redis down")):
            response = await client.post(
                "/public/resource",
                headers={"idempotency-key": "redis-down-key"}
            )
            # The request should still succeed and bypass idempotency (fail open)
            assert response.status_code == 200
            assert response.json()["msg"] == "created"
            assert "X-Cache-Idempotency" not in response.headers
