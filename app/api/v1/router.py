from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit_logs,
    auth,
    companies,
    customers,
    dte,
    health,
    products,
    subscriptions,
    api_keys,
    rbac,
    onboarding,
    superadmin,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit_logs"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(dte.router, prefix="/dte", tags=["dte"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
# Fase 6 — SaaS commercial layer
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api_keys"])
api_router.include_router(rbac.router, prefix="/rbac", tags=["rbac"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
api_router.include_router(superadmin.router, prefix="/superadmin", tags=["superadmin"])
