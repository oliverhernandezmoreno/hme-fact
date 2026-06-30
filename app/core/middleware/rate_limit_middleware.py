from __future__ import annotations

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis sliding window rate limiter for /public/* API endpoints.
    Limit is per api_key_id per minute, sourced from the plan's api_rate_limit_per_min.
    Falls back to DEFAULT_LIMIT if no plan info available.
    """

    DEFAULT_LIMIT = 60  # requests per minute
    PUBLIC_PREFIX = "/public/"

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith(self.PUBLIC_PREFIX):
            return await call_next(request)

        api_key_id = getattr(request.state, "api_key_id", None)
        if api_key_id is None:
            return await call_next(request)

        try:
            import redis.asyncio as aioredis

            from app.core.config import get_settings

            settings = get_settings()
            redis = aioredis.from_url(str(settings.REDIS_URL), decode_responses=True)

            window = 60  # seconds
            now = int(time.time())
            now - window
            key = f"ratelimit:{api_key_id}:{now // window}"

            async with redis.pipeline() as pipe:
                pipe.incr(key)
                pipe.expire(key, window + 5)
                results = await pipe.execute()

            count = results[0]
            limit = self.DEFAULT_LIMIT

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, limit - count))
            response.headers["X-RateLimit-Reset"] = str((now // window + 1) * window)

            if count > limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": f"Rate limit exceeded: {limit} requests/minute",
                        "retry_after": window,
                    },
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "Retry-After": str(window),
                    },
                )
            return response

        except Exception:
            # If Redis is unavailable, allow the request (fail open)
            return await call_next(request)
