from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.db.session import AsyncSessionLocal
from app.modules.apikeys.services.api_key_service import APIKeyService


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Detects X-API-Key header on /public/* routes.
    Validates the key, injects company_id into request.state.
    """

    PUBLIC_PREFIX = "/public/"

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path.startswith(self.PUBLIC_PREFIX):
            raw_key = request.headers.get("X-API-Key")
            if not raw_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "missing_api_key", "message": "X-API-Key header is required"},
                )

            async with AsyncSessionLocal() as session:
                svc = APIKeyService(session)
                api_key = await svc.validate(raw_key)
                if api_key is None:
                    return JSONResponse(
                        status_code=401,
                        content={"error": "invalid_api_key", "message": "Invalid or expired API Key"},
                    )

                # Inject company context into request state
                request.state.company_id = api_key.company_id
                request.state.api_key_id = api_key.id
                request.state.api_key_scopes = api_key.scopes
                request.state.auth_method = "api_key"

        return await call_next(request)
