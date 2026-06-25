from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("", summary="API Public status and usage")
async def get_status(request: Request):
    company_id = getattr(request.state, "company_id", None)
    return {
        "status": "ok",
        "version": "v1",
        "company_id": str(company_id) if company_id else None,
        "authenticated": company_id is not None,
        "docs": "/public/v1/openapi.json",
    }


@router.get("/usage", summary="Get current period API usage for authenticated company")
async def get_usage(request: Request):
    from app.db.session import AsyncSessionLocal
    from app.modules.billing.services.quota_service import QuotaService

    company_id = getattr(request.state, "company_id", None)
    if company_id is None:
        return {"error": "not_authenticated"}

    async with AsyncSessionLocal() as session:
        svc = QuotaService(session)
        summary = await svc.get_usage_summary(company_id)

    if summary is None:
        return {"error": "no_subscription"}

    return {
        "company_id": str(company_id),
        "plan": summary.plan_name,
        "period": f"{summary.period_year}-{summary.period_month:02d}",
        "dtes": {"used": summary.dtes_used, "limit": summary.dtes_limit},
        "api_calls": {"used": summary.api_calls_used, "rate_limit_per_min": summary.api_rate_limit_per_min},
    }
