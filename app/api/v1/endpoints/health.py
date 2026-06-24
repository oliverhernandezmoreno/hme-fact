from __future__ import annotations

import logging
from typing import Any

import redis.asyncio as redis
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import SessionDep
from app.core.config import get_settings
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get("")
async def get_health() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/db")
async def get_health_db(session: SessionDep) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as exc:
        logger.error("DB health check failed", exc_info=exc)
        return {"status": "unhealthy", "error": str(exc)}


@router.get("/redis")
async def get_health_redis() -> dict[str, str]:
    try:
        redis_client = redis.from_url(str(settings.REDIS_URL))
        await redis_client.ping()
        await redis_client.close()
        return {"status": "healthy"}
    except Exception as exc:
        logger.error("Redis health check failed", exc_info=exc)
        return {"status": "unhealthy", "error": str(exc)}


@router.get("/workers")
async def get_health_workers() -> dict[str, Any]:
    try:
        # celery_app.control.ping() is a synchronous call.
        # It broadcasts a ping to all workers. It returns a list of dicts.
        responses = celery_app.control.ping(timeout=1.0)
        return {"status": "healthy" if responses else "unhealthy", "workers": responses}
    except Exception as exc:
        logger.error("Workers health check failed", exc_info=exc)
        return {"status": "unhealthy", "error": str(exc)}
