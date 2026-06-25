from __future__ import annotations

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.db.session import AsyncSessionLocal
from app.modules.billing.services.quota_service import QuotaService


class QuotaMiddleware(BaseHTTPMiddleware):
    """
    Intercepts DTE emission endpoints and checks DTE quota before allowing the request.
    Returns HTTP 402 Payment Required if quota is exceeded.
    Completely decoupled from DTE service logic.
    """

    DTE_EMIT_PATHS = {"/api/v1/dte", "/public/v1/dte"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Only intercept POST to DTE endpoints (emission)
        if request.method == "POST" and any(path.startswith(p) for p in self.DTE_EMIT_PATHS):
            company_id = getattr(request.state, "company_id", None)
            if company_id is not None:
                async with AsyncSessionLocal() as session:
                    quota_svc = QuotaService(session)
                    result = await quota_svc.check_dte_quota(company_id)
                    if not result.allowed:
                        return JSONResponse(
                            status_code=402,
                            content={
                                "error": "quota_exceeded",
                                "message": result.reason,
                                "detail": {
                                    "feature": result.feature,
                                    "used": result.used,
                                    "limit": result.limit,
                                    "usage_pct": result.usage_pct,
                                },
                            },
                        )
                    # Increment usage after successful check — actual increment
                    # happens in the endpoint after successful emission
                    request.state.quota_result = result

        return await call_next(request)
