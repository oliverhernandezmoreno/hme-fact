from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import Subscription, SubscriptionPlan
from app.models.company import Company
from app.models.user import User
from app.repositories.saas_metrics import SaasMetricsRepository
from app.repositories.usage_metric import UsageMetricRepository


class SaasMetricsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = SaasMetricsRepository(session)
        self._usage_repo = UsageMetricRepository(session)

    async def compute_and_save_snapshot(self) -> dict:
        """
        Computes platform-wide KPIs and saves/updates today's snapshot.
        Called by Celery beat task daily at 02:00 UTC.
        """
        today = datetime.now(UTC).date()
        now = datetime.now(UTC)
        month, year = now.month, now.year
        period_label = f"{year:04d}-{month:02d}"

        # --- Companies ---
        active_companies = await self._count_companies_by_status("active")
        trial_companies = await self._count_companies_by_status("trial")
        suspended_companies = await self._count_companies_by_status("suspended")

        # --- Users ---
        total_users_result = await self._session.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        total_users = total_users_result.scalar_one()

        # --- Usage this month ---
        dtes_this_month = await self._usage_repo.get_total_dtes_this_month()
        api_calls_this_month = await self._usage_repo.get_total_api_calls_this_month()

        # --- MRR: sum of active subscription plan prices ---
        mrr_result = await self._session.execute(
            select(func.coalesce(func.sum(SubscriptionPlan.price), 0))
            .join(Subscription, Subscription.plan_id == SubscriptionPlan.id)
            .where(Subscription.status == "active")
        )
        mrr = float(mrr_result.scalar_one())
        arr = mrr * 12

        # --- Plan distribution ---
        dist_result = await self._session.execute(
            select(SubscriptionPlan.code, func.count(Subscription.id))
            .join(Subscription, Subscription.plan_id == SubscriptionPlan.id)
            .where(Subscription.status.in_(["active", "trial"]))
            .group_by(SubscriptionPlan.code)
        )
        plan_distribution = {row[0]: row[1] for row in dist_result}

        # --- Churn / Growth (simplified) ---
        churn_rate = 0.0
        if active_companies > 0:
            churn_rate = round(
                (await self._count_cancelled_this_month()) / max(active_companies, 1) * 100, 4
            )

        data = {
            "period_label": period_label,
            "mrr": mrr,
            "arr": arr,
            "active_companies": active_companies,
            "trial_companies": trial_companies,
            "suspended_companies": suspended_companies,
            "new_companies_this_month": await self._count_new_companies_this_month(),
            "churned_companies_this_month": await self._count_cancelled_this_month(),
            "total_users": total_users,
            "active_users_30d": total_users,  # Simplified: use last_login_at filter in production
            "dtes_this_month": dtes_this_month,
            "api_calls_this_month": api_calls_this_month,
            "churn_rate_pct": churn_rate,
            "growth_rate_pct": 0.0,
            "plan_distribution": plan_distribution,
            "extra": {},
        }

        snapshot = await self._repo.upsert(today, data)
        return data

    async def get_dashboard_summary(self) -> dict:
        """Returns latest snapshot + trend vs previous."""
        latest = await self._repo.get_latest()
        if latest is None:
            return {}
        history = await self._repo.get_historical(days=30)
        return {
            "snapshot_date": str(latest.snapshot_date),
            "mrr": latest.mrr,
            "arr": latest.arr,
            "active_companies": latest.active_companies,
            "trial_companies": latest.trial_companies,
            "suspended_companies": latest.suspended_companies,
            "total_users": latest.total_users,
            "dtes_this_month": latest.dtes_this_month,
            "api_calls_this_month": latest.api_calls_this_month,
            "churn_rate_pct": latest.churn_rate_pct,
            "plan_distribution": latest.plan_distribution,
            "history": [
                {
                    "date": str(s.snapshot_date),
                    "mrr": s.mrr,
                    "active_companies": s.active_companies,
                }
                for s in history[:30]
            ],
        }

    # ── Private helpers ──────────────────────────────────────────────────────

    async def _count_companies_by_status(self, status: str) -> int:
        result = await self._session.execute(
            select(func.count(Subscription.id)).where(Subscription.status == status)
        )
        return result.scalar_one()

    async def _count_new_companies_this_month(self) -> int:
        now = datetime.now(UTC)
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        result = await self._session.execute(
            select(func.count(Company.id)).where(
                Company.created_at >= first_of_month,
                Company.is_active == True,
            )
        )
        return result.scalar_one()

    async def _count_cancelled_this_month(self) -> int:
        now = datetime.now(UTC)
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        result = await self._session.execute(
            select(func.count(Subscription.id)).where(
                Subscription.status == "cancelled",
                Subscription.cancelled_at >= first_of_month,
            )
        )
        return result.scalar_one()
