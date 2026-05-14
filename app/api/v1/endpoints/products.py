from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import SessionDep, TenantDep
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter()


@router.get("", response_model=list[ProductRead])
async def list_products(
    session: SessionDep,
    company_id: TenantDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[ProductRead]:
    products = await ProductRepository(session).list_for_company(
        company_id=company_id,
        offset=offset,
        limit=limit,
    )
    return [ProductRead.model_validate(product) for product in products]


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    session: SessionDep,
    company_id: TenantDep,
) -> ProductRead:
    product = await ProductRepository(session).create(
        {**payload.model_dump(), "company_id": company_id}
    )
    return ProductRead.model_validate(product)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> ProductRead:
    product = await ProductRepository(session).get_for_company(
        company_id=company_id,
        product_id=product_id,
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductRead.model_validate(product)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    session: SessionDep,
    company_id: TenantDep,
) -> ProductRead:
    repo = ProductRepository(session)
    product = await repo.get_for_company(company_id=company_id, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    updated = await repo.update(product, payload.model_dump(exclude_unset=True))
    return ProductRead.model_validate(updated)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> None:
    repo = ProductRepository(session)
    product = await repo.get_for_company(company_id=company_id, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    await repo.delete(product)
