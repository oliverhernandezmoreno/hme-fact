from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    async def get_for_company(
        self,
        *,
        company_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> Product | None:
        result = await self.session.scalars(
            select(Product).where(Product.id == product_id, Product.company_id == company_id)
        )
        return result.first()

    async def list_for_company(
        self,
        *,
        company_id: uuid.UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        result = await self.session.scalars(
            select(Product)
            .where(Product.company_id == company_id)
            .order_by(Product.name)
            .offset(offset)
            .limit(limit)
        )
        return list(result)
