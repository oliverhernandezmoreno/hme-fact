from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models import CompanyUser
from app.repositories.base import BaseRepository


class CompanyUserRepository(BaseRepository[CompanyUser]):
    model = CompanyUser

    async def get_membership(
        self,
        *,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CompanyUser | None:
        result = await self.session.scalars(
            select(CompanyUser).where(
                CompanyUser.company_id == company_id,
                CompanyUser.user_id == user_id,
                CompanyUser.is_active.is_(True),
            )
        )
        return result.first()
