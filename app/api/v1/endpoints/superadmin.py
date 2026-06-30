from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.api.deps import CurrentUserDep, SessionDep
from app.core.deps.rbac import SuperAdminRequired
from app.modules.billing.services.subscription_service import (
    SubscriptionService,
    SubscriptionServiceError,
)
from app.modules.metrics.services.saas_metrics_service import SaasMetricsService

router = APIRouter()


class AssignPlanRequest(BaseModel):
    company_id: uuid.UUID
    plan_code: str


class SuspendRequest(BaseModel):
    reason: str = ""


# ── Companies ─────────────────────────────────────────────────────────────────


@router.get("/companies", dependencies=[SuperAdminRequired], summary="List all companies")
async def list_all_companies(
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: str | None = None,
):
    from sqlalchemy import select

    from app.models.company import Company

    q = select(Company).offset(offset).limit(limit).order_by(Company.created_at.desc())
    if status_filter == "active":
        q = q.where(Company.is_active)
    elif status_filter == "inactive":
        q = q.where(not Company.is_active)
    result = await session.scalars(q)
    companies = list(result)
    return [
        {
            "id": str(c.id),
            "rut": c.rut,
            "legal_name": c.legal_name,
            "is_active": c.is_active,
            "is_onboarding_completed": c.is_onboarding_completed,
            "created_at": c.created_at.isoformat(),
        }
        for c in companies
    ]


@router.put("/companies/{company_id}/suspend", dependencies=[SuperAdminRequired])
async def suspend_company(
    company_id: uuid.UUID,
    body: SuspendRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    svc = SubscriptionService(session)
    try:
        sub = await svc.suspend(company_id, reason=body.reason)
        # Also deactivate the company
        from app.repositories.company import CompanyRepository

        company_repo = CompanyRepository(session)
        company = await company_repo.get(company_id)
        if company:
            await company_repo.update(company, {"is_active": False})
        return {"company_id": str(company_id), "subscription_status": sub.status}
    except SubscriptionServiceError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.put("/companies/{company_id}/activate", dependencies=[SuperAdminRequired])
async def activate_company(
    company_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    from app.repositories.company import CompanyRepository

    company_repo = CompanyRepository(session)
    company = await company_repo.get(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    await company_repo.update(company, {"is_active": True})
    return {"company_id": str(company_id), "is_active": True}


# ── Subscriptions ─────────────────────────────────────────────────────────────


@router.get("/subscriptions", dependencies=[SuperAdminRequired], summary="List all subscriptions")
async def list_all_subscriptions(
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    from app.repositories.subscription_plan import SubscriptionRepository

    repo = SubscriptionRepository(session)
    subs = await repo.get_all_with_plan(offset=offset, limit=limit)
    return [
        {
            "id": str(s.id),
            "company_id": str(s.company_id),
            "status": s.status,
            "plan_code": s.plan.code,
            "plan_name": s.plan.name,
            "current_period_end": s.current_period_end.isoformat(),
            "cancel_at_period_end": s.cancel_at_period_end,
        }
        for s in subs
    ]


@router.post(
    "/subscriptions", dependencies=[SuperAdminRequired], status_code=status.HTTP_201_CREATED
)
async def assign_plan(
    body: AssignPlanRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    svc = SubscriptionService(session)
    try:
        sub = await svc.activate(body.company_id, body.plan_code)
        return {"id": str(sub.id), "status": sub.status}
    except SubscriptionServiceError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


# ── Metrics ───────────────────────────────────────────────────────────────────


@router.get("/metrics", dependencies=[SuperAdminRequired], summary="Global SaaS metrics dashboard")
async def get_global_metrics(session: SessionDep, current_user: CurrentUserDep):
    svc = SaasMetricsService(session)
    return await svc.get_dashboard_summary()


@router.post(
    "/metrics/refresh", dependencies=[SuperAdminRequired], summary="Force refresh metrics snapshot"
)
async def refresh_metrics(session: SessionDep, current_user: CurrentUserDep):
    svc = SaasMetricsService(session)
    data = await svc.compute_and_save_snapshot()
    return {"refreshed": True, "data": data}


# ── Users ─────────────────────────────────────────────────────────────────────


@router.get("/users", dependencies=[SuperAdminRequired], summary="List all platform users")
async def list_all_users(
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    from sqlalchemy import select

    from app.models.user import User

    result = await session.scalars(
        select(User).offset(offset).limit(limit).order_by(User.created_at.desc())
    )
    users = list(result)
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]
