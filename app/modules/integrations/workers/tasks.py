from __future__ import annotations

import asyncio
import uuid

from app.db.session import AsyncSessionLocal
from app.modules.integrations.exceptions import TaxIntegrationError
from app.modules.integrations.services.tax_integration import TaxIntegrationService
from app.modules.integrations.workers.celery_app import celery_app


@celery_app.task(
    name="tax_integrations.send_dte",
    autoretry_for=(TaxIntegrationError,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def send_dte_task(dte_id: str, company_id: str) -> dict[str, str]:
    return asyncio.run(_send_dte(dte_id=dte_id, company_id=company_id))


@celery_app.task(
    name="tax_integrations.poll_dte_status",
    autoretry_for=(TaxIntegrationError,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def poll_dte_status_task(dte_id: str, company_id: str) -> dict[str, str]:
    return asyncio.run(_poll_dte_status(dte_id=dte_id, company_id=company_id))


async def _send_dte(*, dte_id: str, company_id: str) -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        result = await TaxIntegrationService(session).send_dte(
            dte_id=uuid.UUID(dte_id),
            company_id=uuid.UUID(company_id),
        )
        return {
            "dte_id": str(result.dte_id),
            "status": result.status.value,
            "provider": result.provider,
            "external_track_id": result.external_track_id or "",
        }


async def _poll_dte_status(*, dte_id: str, company_id: str) -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        result = await TaxIntegrationService(session).get_status(
            dte_id=uuid.UUID(dte_id),
            company_id=uuid.UUID(company_id),
        )
        return {
            "dte_id": str(result.dte_id),
            "status": result.status.value,
            "provider": result.provider,
            "external_track_id": result.external_track_id or "",
        }
