from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

router = APIRouter()


class CustomerPublicCreate(BaseModel):
    rut: str
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None


@router.get("", summary="List customers (API Key auth)")
async def list_customers(request: Request, offset: int = 0, limit: int = 50):
    from sqlalchemy import select

    from app.db.session import AsyncSessionLocal
    from app.models.customer import Customer

    company_id = request.state.company_id
    async with AsyncSessionLocal() as session:
        result = await session.scalars(
            select(Customer)
            .where(Customer.company_id == company_id)
            .offset(offset)
            .limit(min(limit, 100))
        )
        customers = list(result)
    return [{"id": str(c.id), "rut": c.rut, "name": c.name, "email": c.email} for c in customers]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create customer (API Key auth)")
async def create_customer(body: CustomerPublicCreate, request: Request):
    from app.db.session import AsyncSessionLocal
    from app.repositories.customer import CustomerRepository

    company_id = request.state.company_id
    async with AsyncSessionLocal() as session:
        repo = CustomerRepository(session)
        customer = await repo.create(
            {
                "company_id": company_id,
                "rut": body.rut,
                "name": body.name,
                "email": body.email,
                "phone": body.phone,
                "address": body.address,
            }
        )
    return {"id": str(customer.id), "rut": customer.rut, "name": customer.name}


@router.get("/{customer_id}", summary="Get customer by ID")
async def get_customer(customer_id: str, request: Request):
    import uuid

    from app.db.session import AsyncSessionLocal
    from app.repositories.customer import CustomerRepository

    company_id = request.state.company_id
    async with AsyncSessionLocal() as session:
        repo = CustomerRepository(session)
        try:
            cid = uuid.UUID(customer_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid customer ID")
        customer = await repo.get(cid)
        if customer is None or customer.company_id != company_id:
            raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "id": str(customer.id),
        "rut": customer.rut,
        "name": customer.name,
        "email": customer.email,
    }
