from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUserDep, SessionDep, TenantDep
from app.modules.billing.services.quota_service import QuotaService
from app.modules.billing.services.subscription_service import (
    SubscriptionService,
    SubscriptionServiceError,
)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────


class PlanOut(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: str | None
    price: float
    currency: str
    billing_cycle: str
    trial_days: int
    sort_order: int
    features: dict

    model_config = {"from_attributes": True}


class SubscriptionOut(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool
    plan_code: str
    plan_name: str

    model_config = {"from_attributes": True}


class UsageSummaryOut(BaseModel):
    plan_code: str
    plan_name: str
    period_month: int
    period_year: int
    dtes_used: int
    dtes_limit: int
    api_calls_used: int
    users_used: int
    users_limit: int
    storage_used_bytes: int
    storage_limit_mb: int
    api_access: bool


class ActivateRequest(BaseModel):
    plan_code: str = Field(..., description="Plan code: starter, pyme, business, enterprise")
    trial: bool = False


class ChangePlanRequest(BaseModel):
    plan_code: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/plans", summary="List available subscription plans")
async def list_plans(session: SessionDep):
    from app.repositories.subscription_plan import SubscriptionPlanRepository

    repo = SubscriptionPlanRepository(session)
    plans = await repo.get_active_plans()
    result = []
    for p in plans:
        features = {}
        if p.features:
            features = {
                "dte_limit": p.features.dte_limit,
                "users_limit": p.features.users_limit,
                "branches_limit": p.features.branches_limit,
                "api_access": p.features.api_access,
                "api_rate_limit_per_min": p.features.api_rate_limit_per_min,
                "storage_limit_mb": p.features.storage_limit_mb,
                "support_level": p.features.support_level,
            }
        result.append(
            {
                "id": str(p.id),
                "name": p.name,
                "code": p.code,
                "description": p.description,
                "price": float(p.price),
                "currency": p.currency,
                "billing_cycle": p.billing_cycle,
                "trial_days": p.trial_days,
                "sort_order": p.sort_order,
                "features": features,
            }
        )
    return result


@router.get("/my", summary="Get current subscription for authenticated company")
async def get_my_subscription(
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = SubscriptionService(session)
    current = await svc.get_current(company_id)
    if current is None:
        raise HTTPException(status_code=404, detail="No active subscription")
    sub = current.subscription
    return {
        "id": str(sub.id),
        "company_id": str(sub.company_id),
        "status": sub.status,
        "current_period_start": sub.current_period_start.isoformat(),
        "current_period_end": sub.current_period_end.isoformat(),
        "cancel_at_period_end": sub.cancel_at_period_end,
        "plan_code": current.plan.code,
        "plan_name": current.plan.name,
    }


@router.get("/usage", summary="Get current period usage summary")
async def get_usage(
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = QuotaService(session)
    summary = await svc.get_usage_summary(company_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="No subscription found")
    return {
        "plan_code": summary.plan_code,
        "plan_name": summary.plan_name,
        "period_month": summary.period_month,
        "period_year": summary.period_year,
        "dtes_used": summary.dtes_used,
        "dtes_limit": summary.dtes_limit,
        "api_calls_used": summary.api_calls_used,
        "api_rate_limit_per_min": summary.api_rate_limit_per_min,
        "users_used": summary.users_used,
        "users_limit": summary.users_limit,
        "storage_used_bytes": summary.storage_used_bytes,
        "storage_limit_mb": summary.storage_limit_mb,
        "api_access": summary.api_access,
    }


@router.post(
    "/activate", status_code=status.HTTP_201_CREATED, summary="Activate a subscription plan"
)
async def activate_subscription(
    body: ActivateRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = SubscriptionService(session)
    try:
        sub = await svc.activate(company_id, body.plan_code, trial=body.trial)
        return {"id": str(sub.id), "status": sub.status, "plan_id": str(sub.plan_id)}
    except SubscriptionServiceError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.put("/change-plan", summary="Change subscription plan (upgrade or downgrade)")
async def change_plan(
    body: ChangePlanRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = SubscriptionService(session)
    try:
        sub = await svc.change_plan(company_id, body.plan_code)
        return {"id": str(sub.id), "status": sub.status, "plan_id": str(sub.plan_id)}
    except SubscriptionServiceError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/cancel", summary="Cancel subscription")
async def cancel_subscription(
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
    at_period_end: bool = True,
):
    svc = SubscriptionService(session)
    try:
        sub = await svc.cancel(company_id, at_period_end=at_period_end)
        return {
            "id": str(sub.id),
            "status": sub.status,
            "cancel_at_period_end": sub.cancel_at_period_end,
        }
    except SubscriptionServiceError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get("/billing-events", summary="List billing events for company")
async def list_billing_events(
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    from sqlalchemy import select

    from app.models.billing import BillingEvent

    result = await session.execute(
        select(BillingEvent)
        .where(BillingEvent.company_id == company_id)
        .order_by(BillingEvent.created_at.desc())
        .limit(50)
    )
    events = list(result.scalars())
    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "amount": float(e.amount),
            "currency": e.currency,
            "description": e.description,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
