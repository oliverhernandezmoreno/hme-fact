from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update

from app.models.billing import UsageMetric
from app.repositories.base import BaseRepository


class UsageMetricRepository(BaseRepository[UsageMetric]):
    model = UsageMetric

    def _now(self) -> tuple[int, int]:
        now = datetime.now(UTC)
        return now.month, now.year

    async def get_current_period(self, company_id: uuid.UUID) -> UsageMetric | None:
        month, year = self._now()
        result = await self.session.scalars(
            select(UsageMetric).where(
                UsageMetric.company_id == company_id,
                UsageMetric.period_month == month,
                UsageMetric.period_year == year,
            )
        )
        return result.first()

    async def get_or_create_current(self, company_id: uuid.UUID) -> UsageMetric:
        metric = await self.get_current_period(company_id)
        if metric is None:
            month, year = self._now()
            metric = await self.create(
                {
                    "company_id": company_id,
                    "period_month": month,
                    "period_year": year,
                }
            )
        return metric

    async def increment_dte(self, company_id: uuid.UUID, count: int = 1) -> None:
        month, year = self._now()
        await self.session.execute(
            update(UsageMetric)
            .where(
                UsageMetric.company_id == company_id,
                UsageMetric.period_month == month,
                UsageMetric.period_year == year,
            )
            .values(dtes_emitted=UsageMetric.dtes_emitted + count)
        )
        await self.session.commit()

    async def increment_api_calls(self, company_id: uuid.UUID, count: int = 1) -> None:
        month, year = self._now()
        await self.session.execute(
            update(UsageMetric)
            .where(
                UsageMetric.company_id == company_id,
                UsageMetric.period_month == month,
                UsageMetric.period_year == year,
            )
            .values(api_calls=UsageMetric.api_calls + count)
        )
        await self.session.commit()

    async def get_total_dtes_this_month(self) -> int:
        month, year = self._now()
        result = await self.session.execute(
            select(func.coalesce(func.sum(UsageMetric.dtes_emitted), 0)).where(
                UsageMetric.period_month == month,
                UsageMetric.period_year == year,
            )
        )
        return result.scalar_one()

    async def get_total_api_calls_this_month(self) -> int:
        month, year = self._now()
        result = await self.session.execute(
            select(func.coalesce(func.sum(UsageMetric.api_calls), 0)).where(
                UsageMetric.period_month == month,
                UsageMetric.period_year == year,
            )
        )
        return result.scalar_one()
