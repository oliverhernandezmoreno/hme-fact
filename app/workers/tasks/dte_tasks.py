from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import DTE, DTEEventType, DTEStatus
from app.modules.integrations.services import TaxIntegrationService
from app.modules.notifications.services.email_service import EmailService
from app.modules.pdf.services.pdf_generator import PdfGeneratorService
from app.services.audit import AuditLogService
from app.workers.celery_app import celery_app
from app.workers.utils.async_runner import async_task

logger = logging.getLogger(__name__)


def get_tax_integration_service(session: AsyncSession) -> TaxIntegrationService:
    # Factory for Celery usage
    return TaxIntegrationService(session=session)


@celery_app.task(bind=True, max_retries=3)
@async_task
async def send_dte_task(self: Any, dte_id: str, company_id: str, session: AsyncSession) -> None:
    logger.info("Starting background task: send_dte_task", extra={"dte_id": dte_id})
    try:
        service = get_tax_integration_service(session)
        await service.send_dte(dte_id=uuid.UUID(dte_id), company_id=uuid.UUID(company_id))
    except Exception as exc:
        logger.error("Error in send_dte_task", exc_info=exc)
        self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=5)
@async_task
async def check_dte_status_task(
    self: Any, dte_id: str, company_id: str, session: AsyncSession
) -> None:
    logger.info("Starting background task: check_dte_status_task", extra={"dte_id": dte_id})
    try:
        service = get_tax_integration_service(session)
        await service.get_status(dte_id=uuid.UUID(dte_id), company_id=uuid.UUID(company_id))
    except Exception as exc:
        logger.error("Error in check_dte_status_task", exc_info=exc)
        self.retry(exc=exc, countdown=300)


@celery_app.task(bind=True, max_retries=2)
@async_task
async def generate_dte_pdf_task(
    self: Any, dte_id: str, company_id: str, session: AsyncSession
) -> None:
    logger.info("Starting background task: generate_dte_pdf_task", extra={"dte_id": dte_id})
    try:
        from sqlalchemy import select

        result = await session.execute(
            select(DTE).where(DTE.id == uuid.UUID(dte_id), DTE.company_id == uuid.UUID(company_id))
        )
        dte = result.scalar_one_or_none()
        if not dte:
            logger.error("DTE not found for PDF generation")
            return

        pdf_service = PdfGeneratorService(session)
        await pdf_service.generate_pdf(dte)

        # Update status and audit
        dte.status = DTEStatus.PDF_GENERATED
        audit_service = AuditLogService(session)
        await audit_service.log_action(
            action=DTEEventType.PDF_GENERATED.value,
            entity_type="DTE",
            entity_id=dte.id,
            company_id=dte.company_id,
        )
    except Exception as exc:
        logger.error("Error in generate_dte_pdf_task", exc_info=exc)
        self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
@async_task
async def send_dte_email_task(
    self: Any, dte_id: str, company_id: str, to_email: str, session: AsyncSession
) -> None:
    logger.info(
        "Starting background task: send_dte_email_task", extra={"dte_id": dte_id, "to": to_email}
    )
    try:
        from sqlalchemy import select

        result = await session.execute(
            select(DTE)
            .where(DTE.id == uuid.UUID(dte_id), DTE.company_id == uuid.UUID(company_id))
            .options(selectinload(DTE.company), selectinload(DTE.customer))
        )
        dte = result.scalar_one_or_none()
        if not dte:
            logger.error("DTE not found for email sending")
            return

        # Fetch files from storage
        from app.services.storage import get_file_storage_service

        storage = get_file_storage_service()

        pdf_path = f"companies/{dte.company_id}/dtes/{dte.id}/dte_{dte.folio}.pdf"
        try:
            pdf_content = await storage.get_file(pdf_path)
        except FileNotFoundError:
            pdf_content = None

        email_service = EmailService()

        # Simple HTML template for the email (we could also use jinja here)
        html_content = f"""
        <html><body>
            <h2>Documento Tributario Electrónico</h2>
            <p>Estimado(a) {dte.customer.legal_name if dte.customer else "Cliente"},</p>
            <p>Se ha emitido el documento tipo {dte.dte_type} N° {dte.folio}.</p>
            <p>Total: ${dte.total_amount}</p>
        </body></html>
        """

        success = email_service.send_dte_notification(
            to_email=to_email,
            subject=f"DTE N° {dte.folio} - {dte.company.legal_name if dte.company else ''}",
            html_content=html_content,
            pdf_content=pdf_content,
            folio=dte.folio,
        )

        if success:
            dte.status = DTEStatus.EMAILED
            audit_service = AuditLogService(session)
            await audit_service.log_action(
                action=DTEEventType.EMAILED.value,
                entity_type="DTE",
                entity_id=dte.id,
                company_id=dte.company_id,
            )
        else:
            raise RuntimeError("Email provider failed to send email")

    except Exception as exc:
        logger.error("Error in send_dte_email_task", exc_info=exc)
        self.retry(exc=exc, countdown=120)


@celery_app.task
@async_task
async def retry_failed_dtes_task(session: AsyncSession) -> None:
    logger.info("Running scheduled task: retry_failed_dtes_task")
    try:
        # Retry DTEs in ERROR or CONTINGENCY status
        from sqlalchemy import or_, select

        result = await session.execute(
            select(DTE).where(
                or_(DTE.status == DTEStatus.ERROR, DTE.status == DTEStatus.CONTINGENCY)
            )
        )
        dtes = result.scalars().all()
        for dte in dtes:
            if dte.sii_xml:
                from app.workers.tasks.dte_emission import emit_dte_task

                emit_dte_task.delay(str(dte.id))
            else:
                send_dte_task.delay(str(dte.id), str(dte.company_id))
    except Exception as exc:
        logger.error("Error in retry_failed_dtes_task", exc_info=exc)
