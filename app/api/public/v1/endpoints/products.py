from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("", summary="List products (API Key auth)")
async def list_products(request: Request, offset: int = 0, limit: int = 50):
    from sqlalchemy import select

    from app.db.session import AsyncSessionLocal
    from app.models.product import Product

    company_id = request.state.company_id
    async with AsyncSessionLocal() as session:
        result = await session.scalars(
            select(Product)
            .where(Product.company_id == company_id)
            .offset(offset)
            .limit(min(limit, 100))
        )
        products = list(result)
    return [
        {"id": str(p.id), "code": p.code, "name": p.name, "price": float(p.price), "unit": p.unit}
        for p in products
    ]


@router.get("/{product_id}", summary="Get product by ID")
async def get_product(product_id: str, request: Request):
    import uuid

    from fastapi import HTTPException

    from app.db.session import AsyncSessionLocal
    from app.repositories.product import ProductRepository

    company_id = request.state.company_id
    async with AsyncSessionLocal() as session:
        repo = ProductRepository(session)
        try:
            pid = uuid.UUID(product_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid product ID")
        product = await repo.get(pid)
        if product is None or product.company_id != company_id:
            raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": str(product.id),
        "code": product.code,
        "name": product.name,
        "price": float(product.price),
    }
