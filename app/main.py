from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.public.v1.router import public_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware.api_key_middleware import APIKeyMiddleware
from app.core.middleware.quota_middleware import QuotaMiddleware
from app.core.middleware.rate_limit_middleware import RateLimitMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="hmEFact — Plataforma SaaS Facturación Electrónica Chile",
        description="API de facturación electrónica SaaS multiempresa con integración SII.",
        version="6.0.0",
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ────────────────────────────────────────────────────────────────
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ── Middleware (order matters: last added = first executed) ─────────────
    app.add_middleware(QuotaMiddleware)       # Blocks DTE emission if quota exceeded
    app.add_middleware(RateLimitMiddleware)   # Rate limits /public/* by API Key
    app.add_middleware(APIKeyMiddleware)      # Authenticates /public/* with X-API-Key

    # ── Exception handlers ──────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Internal API (JWT auth) ─────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # ── Public API (API Key auth) ────────────────────────────────────────────
    app.include_router(public_router, prefix="/public/v1")

    # ── Health ───────────────────────────────────────────────────────────────
    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": "6.0.0"}

    return app


app = create_app()
