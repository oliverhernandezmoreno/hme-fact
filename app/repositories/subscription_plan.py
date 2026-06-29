from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from app.models.billing import Subscription, SubscriptionPlan
from app.repositories.base import BaseRepository


class SubscriptionPlanRepository(BaseRepository[SubscriptionPlan]):
    model = SubscriptionPlan

    async def get_by_code(self, code: str) -> SubscriptionPlan | None:
        result = await self.session.scalars(
            select(SubscriptionPlan).where(SubscriptionPlan.code == code)
        )
        return result.first()

    async def get_active_plans(self) -> list[SubscriptionPlan]:
        result = await self.session.scalars(
            select(SubscriptionPlan)
            .options(joinedload(SubscriptionPlan.features))
            .where(SubscriptionPlan.is_active == True, SubscriptionPlan.is_public == True)
            .order_by(SubscriptionPlan.sort_order)
        )
        return list(result.unique())

    async def get_with_features(self, plan_id: uuid.UUID) -> SubscriptionPlan | None:
        result = await self.session.scalars(
            select(SubscriptionPlan)
            .options(joinedload(SubscriptionPlan.features))
            .where(SubscriptionPlan.id == plan_id)
        )
        return result.first()


class SubscriptionRepository(BaseRepository[Subscription]):
    model = Subscription

    async def get_by_company(self, company_id: uuid.UUID) -> Subscription | None:
        result = await self.session.scalars(
            select(Subscription)
            .options(joinedload(Subscription.plan).joinedload(SubscriptionPlan.features))
            .where(Subscription.company_id == company_id)
        )
        return result.first()

    async def get_active(self, company_id: uuid.UUID) -> Subscription | None:
        result = await self.session.scalars(
            select(Subscription)
            .options(joinedload(Subscription.plan).joinedload(SubscriptionPlan.features))
            .where(
                Subscription.company_id == company_id,
                Subscription.status.in_(["active", "trial"]),
            )
        )
        return result.first()

    async def get_expiring_soon(self, hours: int = 48) -> list[Subscription]:
        """Returns subscriptions expiring within the next N hours."""
        from datetime import timedelta

        cutoff = datetime.now(UTC) + timedelta(hours=hours)
        result = await self.session.scalars(
            select(Subscription).where(
                Subscription.status == "active",
                Subscription.current_period_end <= cutoff,
                Subscription.cancel_at_period_end == False,
            )
        )
        return list(result)

    async def expire_subscriptions(self) -> int:
        """Marks past-due active subscriptions as expired. Returns count."""
        now = datetime.now(UTC)
        result = await self.session.execute(
            update(Subscription)
            .where(
                Subscription.status == "active",
                Subscription.current_period_end < now,
            )
            .values(status="expired")
        )
        await self.session.commit()
        return result.rowcount  # type: ignore[return-value]

    async def get_all_with_plan(self, *, offset: int = 0, limit: int = 100) -> list[Subscription]:
        result = await self.session.scalars(
            select(Subscription).options(joinedload(Subscription.plan)).offset(offset).limit(limit)
        )
        return list(result.unique())
