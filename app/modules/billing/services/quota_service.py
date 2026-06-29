from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.subscription_plan import SubscriptionPlanRepository, SubscriptionRepository
from app.repositories.usage_metric import UsageMetricRepository


@dataclass
class QuotaResult:
    allowed: bool
    used: int
    limit: int
    feature: str
    reason: str = ""

    @property
    def remaining(self) -> int:
        if self.limit == -1:
            return -1  # unlimited
        return max(0, self.limit - self.used)

    @property
    def usage_pct(self) -> float:
        if self.limit <= 0:
            return 0.0
        return round(self.used / self.limit * 100, 2)


@dataclass
class UsageSummary:
    company_id: uuid.UUID
    plan_code: str
    plan_name: str
    period_month: int
    period_year: int
    dtes_used: int
    dtes_limit: int
    api_calls_used: int
    api_rate_limit_per_min: int
    users_used: int
    users_limit: int
    storage_used_bytes: int
    storage_limit_mb: int
    api_access: bool


class QuotaExceededError(Exception):
    def __init__(self, result: QuotaResult) -> None:
        self.result = result
        super().__init__(result.reason)


class QuotaService:
    """
    Controls consumption quotas.
    Called by middleware BEFORE endpoint logic — DTE service never needs to know about billing.
    Redis is used for rate limiting; DB is the source of truth for monthly totals.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._sub_repo = SubscriptionRepository(session)
        self._plan_repo = SubscriptionPlanRepository(session)
        self._usage_repo = UsageMetricRepository(session)

    async def check_dte_quota(self, company_id: uuid.UUID) -> QuotaResult:
        sub = await self._sub_repo.get_active(company_id)
        if sub is None:
            return QuotaResult(
                allowed=False,
                used=0,
                limit=0,
                feature="dte_limit",
                reason="No active subscription",
            )

        features = sub.plan.features
        limit = features.dte_limit if features else 0
        metric = await self._usage_repo.get_or_create_current(company_id)
        used = metric.dtes_emitted

        if limit == -1:  # unlimited plan
            return QuotaResult(allowed=True, used=used, limit=limit, feature="dte_limit")

        allowed = used < limit
        return QuotaResult(
            allowed=allowed,
            used=used,
            limit=limit,
            feature="dte_limit",
            reason="" if allowed else f"DTE quota exceeded ({used}/{limit} used this month)",
        )

    async def check_api_access(self, company_id: uuid.UUID) -> QuotaResult:
        sub = await self._sub_repo.get_active(company_id)
        if sub is None:
            return QuotaResult(
                allowed=False,
                used=0,
                limit=0,
                feature="api_access",
                reason="No active subscription",
            )
        features = sub.plan.features
        has_access = features.api_access if features else False
        return QuotaResult(
            allowed=has_access,
            used=0,
            limit=1 if has_access else 0,
            feature="api_access",
            reason="" if has_access else "API access not included in your plan",
        )

    async def check_user_quota(self, company_id: uuid.UUID, current_user_count: int) -> QuotaResult:
        sub = await self._sub_repo.get_active(company_id)
        if sub is None:
            return QuotaResult(
                allowed=False,
                used=0,
                limit=0,
                feature="users_limit",
                reason="No active subscription",
            )

        features = sub.plan.features
        limit = features.users_limit if features else 0

        if limit == -1:
            return QuotaResult(
                allowed=True, used=current_user_count, limit=limit, feature="users_limit"
            )

        allowed = current_user_count < limit
        return QuotaResult(
            allowed=allowed,
            used=current_user_count,
            limit=limit,
            feature="users_limit",
            reason="" if allowed else f"User quota exceeded ({current_user_count}/{limit})",
        )

    async def increment_dte_usage(self, company_id: uuid.UUID) -> None:
        await self._usage_repo.get_or_create_current(company_id)
        await self._usage_repo.increment_dte(company_id)

    async def increment_api_usage(self, company_id: uuid.UUID) -> None:
        await self._usage_repo.get_or_create_current(company_id)
        await self._usage_repo.increment_api_calls(company_id)

    async def get_usage_summary(self, company_id: uuid.UUID) -> UsageSummary | None:
        sub = await self._sub_repo.get_active(company_id)
        if sub is None:
            return None

        features = sub.plan.features
        metric = await self._usage_repo.get_or_create_current(company_id)

        return UsageSummary(
            company_id=company_id,
            plan_code=sub.plan.code,
            plan_name=sub.plan.name,
            period_month=metric.period_month,
            period_year=metric.period_year,
            dtes_used=metric.dtes_emitted,
            dtes_limit=features.dte_limit if features else 0,
            api_calls_used=metric.api_calls,
            api_rate_limit_per_min=features.api_rate_limit_per_min if features else 0,
            users_used=metric.active_users,
            users_limit=features.users_limit if features else 0,
            storage_used_bytes=metric.storage_used_bytes,
            storage_limit_mb=features.storage_limit_mb if features else 0,
            api_access=features.api_access if features else False,
        )
