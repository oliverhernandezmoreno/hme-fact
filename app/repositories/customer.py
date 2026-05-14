from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    model = Customer

    async def get_for_company(
        self,
        *,
        company_id: uuid.UUID,
        customer_id: uuid.UUID,
    ) -> Customer | None:
        result = await self.session.scalars(
            select(Customer).where(Customer.id == customer_id, Customer.company_id == company_id)
        )
        return result.first()

    async def list_for_company(
        self,
        *,
        company_id: uuid.UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        result = await self.session.scalars(
            select(Customer)
            .where(Customer.company_id == company_id)
            .order_by(Customer.legal_name)
            .offset(offset)
            .limit(limit)
        )
        return list(result)
