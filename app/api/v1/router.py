from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import auth, companies, customers, dte, products

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(dte.router, prefix="/dte", tags=["dte"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
