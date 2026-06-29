from __future__ import annotations

from datetime import UTC, date

from sqlalchemy import desc, select

from app.models.saas_metrics import SaasMetricsSnapshot
from app.repositories.base import BaseRepository


class SaasMetricsRepository(BaseRepository[SaasMetricsSnapshot]):
    model = SaasMetricsSnapshot

    async def get_by_date(self, snapshot_date: date) -> SaasMetricsSnapshot | None:
        result = await self.session.scalars(
            select(SaasMetricsSnapshot).where(SaasMetricsSnapshot.snapshot_date == snapshot_date)
        )
        return result.first()

    async def get_latest(self) -> SaasMetricsSnapshot | None:
        result = await self.session.scalars(
            select(SaasMetricsSnapshot).order_by(desc(SaasMetricsSnapshot.snapshot_date)).limit(1)
        )
        return result.first()

    async def get_historical(self, days: int = 90) -> list[SaasMetricsSnapshot]:
        from datetime import datetime, timedelta

        cutoff = datetime.now(UTC).date() - timedelta(days=days)
        result = await self.session.scalars(
            select(SaasMetricsSnapshot)
            .where(SaasMetricsSnapshot.snapshot_date >= cutoff)
            .order_by(desc(SaasMetricsSnapshot.snapshot_date))
        )
        return list(result)

    async def upsert(self, snapshot_date: date, data: dict) -> SaasMetricsSnapshot:
        existing = await self.get_by_date(snapshot_date)
        if existing:
            return await self.update(existing, data)
        data["snapshot_date"] = snapshot_date
        return await self.create(data)
