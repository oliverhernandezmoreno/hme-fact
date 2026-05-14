from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import SessionDep, TenantDep
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate

router = APIRouter()


@router.get("", response_model=list[CustomerRead])
async def list_customers(
    session: SessionDep,
    company_id: TenantDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[CustomerRead]:
    customers = await CustomerRepository(session).list_for_company(
        company_id=company_id,
        offset=offset,
        limit=limit,
    )
    return [CustomerRead.model_validate(customer) for customer in customers]


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    session: SessionDep,
    company_id: TenantDep,
) -> CustomerRead:
    customer = await CustomerRepository(session).create(
        {**payload.model_dump(), "company_id": company_id}
    )
    return CustomerRead.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> CustomerRead:
    customer = await CustomerRepository(session).get_for_company(
        company_id=company_id,
        customer_id=customer_id,
    )
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return CustomerRead.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    session: SessionDep,
    company_id: TenantDep,
) -> CustomerRead:
    repo = CustomerRepository(session)
    customer = await repo.get_for_company(company_id=company_id, customer_id=customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    updated = await repo.update(customer, payload.model_dump(exclude_unset=True))
    return CustomerRead.model_validate(updated)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> None:
    repo = CustomerRepository(session)
    customer = await repo.get_for_company(company_id=company_id, customer_id=customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    await repo.delete(customer)
