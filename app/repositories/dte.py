from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import DTE, DTEXml
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

    async def get_for_tax_integration(
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
                selectinload(DTE.xml_documents),
            )
        )
        return result.first()

    async def get_latest_xml(self, dte_id: uuid.UUID) -> DTEXml | None:
        result = await self.session.scalars(
            select(DTEXml)
            .where(DTEXml.dte_id == dte_id)
            .order_by(DTEXml.created_at.desc())
            .limit(1)
        )
        return result.first()
