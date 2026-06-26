from __future__ import annotations

import redis.asyncio as redis
from fastapi import APIRouter
from app.api.deps import CurrentUserDep
from app.core.deps.rbac import SuperAdminRequired
from app.services.sii.circuit_breaker import SIICircuitBreaker
from app.core.config import get_settings

router = APIRouter()


@router.get("/status", dependencies=[SuperAdminRequired], summary="Get SII Circuit Breaker status")
async def get_sii_circuit_breaker_status(current_user: CurrentUserDep):
    cb = SIICircuitBreaker()
    return await cb.get_status_details()


@router.post("/reset", dependencies=[SuperAdminRequired], summary="Reset SII Circuit Breaker state to CLOSED")
async def reset_sii_circuit_breaker(current_user: CurrentUserDep):
    cb = SIICircuitBreaker()
    await cb.reset()
    return {
        "message": "Circuit breaker has been manually reset to CLOSED",
        "status": await cb.get_status_details()
    }


@router.post("/simulate-failure", dependencies=[SuperAdminRequired], summary="Simulate SII Web Services failure")
async def simulate_sii_failure(current_user: CurrentUserDep):
    settings = get_settings()
    r = redis.from_url(str(settings.REDIS_URL), decode_responses=True)
    try:
        await r.set("sii:cb:simulate_failure", "true")
        return {"message": "SII failure simulation enabled successfully"}
    finally:
        await r.aclose()


@router.post("/clear-failure-simulation", dependencies=[SuperAdminRequired], summary="Clear simulated SII Web Services failure")
async def clear_sii_failure_simulation(current_user: CurrentUserDep):
    settings = get_settings()
    r = redis.from_url(str(settings.REDIS_URL), decode_responses=True)
    try:
        await r.delete("sii:cb:simulate_failure")
        return {"message": "SII failure simulation disabled successfully"}
    finally:
        await r.aclose()
