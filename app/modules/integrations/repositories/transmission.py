from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models import DTETransmission
from app.repositories.base import BaseRepository


class DTETransmissionRepository(BaseRepository[DTETransmission]):
    model = DTETransmission

    async def get_latest_for_dte(self, dte_id: uuid.UUID) -> DTETransmission | None:
        result = await self.session.scalars(
            select(DTETransmission)
            .where(DTETransmission.dte_id == dte_id)
            .order_by(DTETransmission.created_at.desc())
            .limit(1)
        )
        return result.first()

    async def get_latest_with_track_id(self, dte_id: uuid.UUID) -> DTETransmission | None:
        result = await self.session.scalars(
            select(DTETransmission)
            .where(DTETransmission.dte_id == dte_id, DTETransmission.external_track_id.is_not(None))
            .order_by(DTETransmission.created_at.desc())
            .limit(1)
        )
        return result.first()

    def add(self, entity: DTETransmission) -> DTETransmission:
        self.session.add(entity)
        return entity
