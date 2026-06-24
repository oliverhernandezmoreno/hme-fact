from __future__ import annotations

from app.models import DTEStatusHistory
from app.repositories.base import BaseRepository


class DTEStatusHistoryRepository(BaseRepository[DTEStatusHistory]):
    model = DTEStatusHistory

    def add(self, entity: DTEStatusHistory) -> DTEStatusHistory:
        self.session.add(entity)
        return entity
