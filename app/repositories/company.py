from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models import Company, CompanyUser
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    model = Company

    async def list_for_user(self, user_id: uuid.UUID) -> list[Company]:
        result = await self.session.scalars(
            select(Company)
            .join(CompanyUser)
            .where(CompanyUser.user_id == user_id, CompanyUser.is_active.is_(True))
            .order_by(Company.legal_name)
        )
        return list(result)
