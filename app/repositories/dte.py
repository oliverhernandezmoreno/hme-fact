from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import DTE
from app.repositories.base import BaseRepository


class DTERepository(BaseRepository[DTE]):
    model = DTE

    async def get_with_xml_dependencies(
        self,
        *,
        dte_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> DTE | None:
        result = await self.session.scalars(
            select(DTE)
            .where(DTE.id == dte_id, DTE.company_id == company_id)
            .options(
                selectinload(DTE.company),
                selectinload(DTE.customer),
                selectinload(DTE.items),
                selectinload(DTE.caf_file),
                selectinload(DTE.certificate),
            )
        )
        return result.first()
