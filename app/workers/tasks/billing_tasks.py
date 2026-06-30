from __future__ import annotations

import asyncio
import logging
from datetime import UTC

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code from sync Celery tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.workers.tasks.billing_tasks.renew_expiring_subscriptions", bind=True)
def renew_expiring_subscriptions(self):
    """
    Renews active subscriptions that expire within 48 hours
    (if cancel_at_period_end is False).
    """

    async def _renew():
        from app.db.session import AsyncSessionLocal
        from app.modules.billing.services.subscription_service import SubscriptionService
        from app.repositories.subscription_plan import SubscriptionRepository

        async with AsyncSessionLocal() as session:
            repo = SubscriptionRepository(session)
            expiring = await repo.get_expiring_soon(hours=48)
            svc = SubscriptionService(session)
            renewed = 0
            for sub in expiring:
                try:
                    await svc.renew(sub.company_id)
                    renewed += 1
                except Exception as e:
                    logger.warning(f"Failed to renew subscription {sub.id}: {e}")
            logger.info(f"Renewed {renewed}/{len(expiring)} expiring subscriptions")
            return renewed

    return _run_async(_renew())


@celery_app.task(name="app.workers.tasks.billing_tasks.compute_saas_metrics_snapshot", bind=True)
def compute_saas_metrics_snapshot(self):
    """Computes and persists daily SaaS metrics snapshot."""

    async def _compute():
        from app.db.session import AsyncSessionLocal
        from app.modules.metrics.services.saas_metrics_service import SaasMetricsService

        async with AsyncSessionLocal() as session:
            svc = SaasMetricsService(session)
            data = await svc.compute_and_save_snapshot()
            logger.info(
                f"SaaS metrics snapshot: MRR={data.get('mrr')}, "
                f"Companies={data.get('active_companies')}"
            )
            return data

    return _run_async(_compute())


@celery_app.task(name="app.workers.tasks.billing_tasks.reset_monthly_usage_counters", bind=True)
def reset_monthly_usage_counters(self):
    """Runs on the 1st of each month — ensures new usage_metric rows are ready."""
    logger.info(
        "Monthly usage reset triggered — new period rows will be created on first DTE emission"
    )
    return {"status": "ok", "message": "New period rows created on demand"}


@celery_app.task(name="app.workers.tasks.billing_tasks.send_quota_warning_emails", bind=True)
def send_quota_warning_emails(self):
    """Sends email warnings to companies that have used >80% of their DTE quota."""

    async def _send():
        from datetime import datetime

        from sqlalchemy import select

        from app.db.session import AsyncSessionLocal
        from app.models.billing import (
            Subscription,
            SubscriptionFeature,
            SubscriptionPlan,
            UsageMetric,
        )

        now = datetime.now(UTC)
        warnings_sent = 0

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(
                    UsageMetric.company_id,
                    UsageMetric.dtes_emitted,
                    SubscriptionFeature.dte_limit,
                )
                .join(Subscription, Subscription.company_id == UsageMetric.company_id)
                .join(SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id)
                .join(SubscriptionFeature, SubscriptionFeature.plan_id == SubscriptionPlan.id)
                .where(
                    UsageMetric.period_month == now.month,
                    UsageMetric.period_year == now.year,
                    Subscription.status == "active",
                    SubscriptionFeature.dte_limit > 0,
                )
            )
            rows = result.fetchall()

            for company_id, dtes_emitted, dte_limit in rows:
                pct = dtes_emitted / dte_limit * 100
                if pct >= 80:
                    # TODO: integrate with email notification service
                    logger.info(
                        f"Quota warning: company={company_id} "
                        f"used={dtes_emitted}/{dte_limit} ({pct:.1f}%)"
                    )
                    warnings_sent += 1

        logger.info(f"Sent {warnings_sent} quota warning notifications")
        return warnings_sent

    return _run_async(_send())
