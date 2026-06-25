from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import BillingEvent, Subscription, SubscriptionPlan
from app.repositories.subscription_plan import SubscriptionPlanRepository, SubscriptionRepository
from app.repositories.usage_metric import UsageMetricRepository


@dataclass
class SubscriptionWithFeatures:
    subscription: Subscription
    plan: SubscriptionPlan
    usage_dtes: int
    usage_api_calls: int
    usage_users: int


class SubscriptionServiceError(Exception):
    pass


class SubscriptionService:
    """
    Manages subscription lifecycle: activation, suspension, renewal, plan changes.
    Desacoplado de JWT y de lógica DTE — solo conoce Company + Plan.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._plan_repo = SubscriptionPlanRepository(session)
        self._sub_repo = SubscriptionRepository(session)
        self._usage_repo = UsageMetricRepository(session)

    async def get_current(self, company_id: uuid.UUID) -> SubscriptionWithFeatures | None:
        sub = await self._sub_repo.get_active(company_id)
        if sub is None:
            return None
        metric = await self._usage_repo.get_current_period(company_id)
        return SubscriptionWithFeatures(
            subscription=sub,
            plan=sub.plan,
            usage_dtes=metric.dtes_emitted if metric else 0,
            usage_api_calls=metric.api_calls if metric else 0,
            usage_users=metric.active_users if metric else 0,
        )

    async def activate(
        self,
        company_id: uuid.UUID,
        plan_code: str,
        *,
        trial: bool = False,
    ) -> Subscription:
        plan = await self._plan_repo.get_by_code(plan_code)
        if plan is None:
            raise SubscriptionServiceError(f"Plan '{plan_code}' not found")
        if not plan.is_active:
            raise SubscriptionServiceError(f"Plan '{plan_code}' is not active")

        existing = await self._sub_repo.get_by_company(company_id)
        if existing and existing.status == "active":
            raise SubscriptionServiceError("Company already has an active subscription")

        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days=30)
        trial_end = now + timedelta(days=plan.trial_days) if trial and plan.trial_days > 0 else None

        if existing:
            sub = await self._sub_repo.update(
                existing,
                {
                    "plan_id": plan.id,
                    "status": "trial" if trial else "active",
                    "current_period_start": now,
                    "current_period_end": period_end,
                    "trial_end": trial_end,
                    "cancel_at_period_end": False,
                    "cancelled_at": None,
                },
            )
        else:
            sub = await self._sub_repo.create(
                {
                    "company_id": company_id,
                    "plan_id": plan.id,
                    "status": "trial" if trial else "active",
                    "current_period_start": now,
                    "current_period_end": period_end,
                    "trial_end": trial_end,
                }
            )

        await self._ensure_usage_metric(company_id)
        await self._record_billing_event(
            company_id=company_id,
            subscription_id=sub.id,
            event_type="trial_start" if trial else "activation",
            amount=Decimal("0") if trial else Decimal(str(plan.price)),
            currency=plan.currency,
            description=f"Plan {plan.name} {'(trial)' if trial else ''} activated",
        )
        return sub

    async def suspend(self, company_id: uuid.UUID, reason: str = "") -> Subscription:
        sub = await self._sub_repo.get_active(company_id)
        if sub is None:
            raise SubscriptionServiceError("No active subscription found")
        updated = await self._sub_repo.update(sub, {"status": "suspended"})
        await self._record_billing_event(
            company_id=company_id,
            subscription_id=sub.id,
            event_type="suspension",
            amount=Decimal("0"),
            currency=sub.plan.currency,
            description=f"Suspended: {reason}",
        )
        return updated

    async def cancel(
        self, company_id: uuid.UUID, *, at_period_end: bool = True
    ) -> Subscription:
        sub = await self._sub_repo.get_active(company_id)
        if sub is None:
            raise SubscriptionServiceError("No active subscription found")
        now = datetime.now(timezone.utc)
        if at_period_end:
            updated = await self._sub_repo.update(sub, {"cancel_at_period_end": True, "cancelled_at": now})
        else:
            updated = await self._sub_repo.update(sub, {"status": "cancelled", "cancelled_at": now})
        await self._record_billing_event(
            company_id=company_id,
            subscription_id=sub.id,
            event_type="cancellation",
            amount=Decimal("0"),
            currency=sub.plan.currency,
            description="Subscription cancelled" + (" at period end" if at_period_end else " immediately"),
        )
        return updated

    async def renew(self, company_id: uuid.UUID) -> Subscription:
        sub = await self._sub_repo.get_by_company(company_id)
        if sub is None:
            raise SubscriptionServiceError("No subscription found")
        if sub.cancel_at_period_end:
            raise SubscriptionServiceError("Subscription is set to cancel at period end")

        now = datetime.now(timezone.utc)
        new_end = now + timedelta(days=30)
        updated = await self._sub_repo.update(
            sub,
            {
                "status": "active",
                "current_period_start": now,
                "current_period_end": new_end,
                "trial_end": None,
            },
        )
        await self._record_billing_event(
            company_id=company_id,
            subscription_id=sub.id,
            event_type="renewal",
            amount=Decimal(str(sub.plan.price)),
            currency=sub.plan.currency,
            description=f"Plan {sub.plan.name} renewed",
        )
        return updated

    async def change_plan(
        self, company_id: uuid.UUID, new_plan_code: str
    ) -> Subscription:
        sub = await self._sub_repo.get_active(company_id)
        if sub is None:
            raise SubscriptionServiceError("No active subscription found")

        new_plan = await self._plan_repo.get_by_code(new_plan_code)
        if new_plan is None:
            raise SubscriptionServiceError(f"Plan '{new_plan_code}' not found")

        old_plan = sub.plan
        event_type = (
            "upgrade"
            if float(new_plan.price) > float(old_plan.price)
            else "downgrade"
        )

        updated = await self._sub_repo.update(
            sub,
            {
                "plan_id": new_plan.id,
                "upgraded_from_plan_id": old_plan.id,
            },
        )
        await self._record_billing_event(
            company_id=company_id,
            subscription_id=sub.id,
            event_type=event_type,
            amount=Decimal(str(new_plan.price)),
            currency=new_plan.currency,
            description=f"Plan changed: {old_plan.name} → {new_plan.name}",
            metadata={"from_plan": old_plan.code, "to_plan": new_plan.code},
        )
        return updated

    # ── Private helpers ─────────────────────────────────────────────────────

    async def _ensure_usage_metric(self, company_id: uuid.UUID) -> None:
        await self._usage_repo.get_or_create_current(company_id)

    async def _record_billing_event(
        self,
        *,
        company_id: uuid.UUID,
        subscription_id: uuid.UUID,
        event_type: str,
        amount: Decimal,
        currency: str,
        description: str = "",
        metadata: dict | None = None,
    ) -> None:
        event = BillingEvent(
            company_id=company_id,
            subscription_id=subscription_id,
            event_type=event_type,
            amount=float(amount),
            currency=currency,
            description=description,
            metadata=metadata or {},
        )
        self._session.add(event)
        await self._session.commit()
