from __future__ import annotations

from fastapi import APIRouter

from app.api.public.v1.endpoints import customers, products, dte, status

public_router = APIRouter()

# All routes under /public/v1 — authenticated by APIKeyMiddleware
public_router.include_router(customers.router, prefix="/customers", tags=["public:customers"])
public_router.include_router(products.router, prefix="/products", tags=["public:products"])
public_router.include_router(dte.router, prefix="/dte", tags=["public:dte"])
public_router.include_router(status.router, prefix="/status", tags=["public:status"])
