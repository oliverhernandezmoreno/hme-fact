from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime, timedelta

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code from sync Celery tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def dispatch_company_webhook(
    session, company_id: uuid.UUID, event_type: str, payload: dict
) -> None:
    from sqlalchemy import select

    from app.models.integration import WebhookSubscription
    from app.workers.integration_worker import send_outbound_webhook

    result = await session.execute(
        select(WebhookSubscription).where(
            WebhookSubscription.company_id == company_id, WebhookSubscription.is_active == True
        )
    )
    subscriptions = result.scalars().all()
    for sub in subscriptions:
        # Check if event_types is empty (all events) or explicitly contains the event_type
        event_list = sub.event_types or []
        if not event_list or event_type in event_list:
            send_outbound_webhook.delay(str(sub.id), event_type, payload)


async def get_company_recipient_emails(session, company_id: uuid.UUID) -> list[str]:
    from sqlalchemy import select

    from app.models.company_user import CompanyUser
    from app.models.user import User

    result = await session.execute(
        select(User.email)
        .join(CompanyUser, CompanyUser.user_id == User.id)
        .where(CompanyUser.company_id == company_id, CompanyUser.is_active == True)
    )
    return [row[0] for row in result.fetchall() if row[0]]


@celery_app.task(name="app.workers.tasks.alert_tasks.check_expiring_certificates_task", bind=True)
def check_expiring_certificates_task(self):
    """Daily check for certificates that expire in less than 30 days."""

    async def _check():
        from sqlalchemy import select

        from app.db.session import AsyncSessionLocal
        from app.models.certificate import Certificate
        from app.models.company import Company
        from app.modules.notifications.services.email_service import EmailService

        now = datetime.now(UTC)
        thirty_days_later = now + timedelta(days=30)
        alerts_triggered = 0

        async with AsyncSessionLocal() as session:
            # Query active certificates expiring within 30 days
            result = await session.execute(
                select(Certificate)
                .join(Company, Company.id == Certificate.company_id)
                .where(
                    Certificate.is_active == True,
                    Certificate.valid_until <= thirty_days_later,
                    Company.is_active == True,
                )
            )
            certificates = result.scalars().all()

            email_service = EmailService()

            for cert in certificates:
                # Calculate remaining days
                days_left = (cert.valid_until - now).days

                # Fetch users to notify
                emails = await get_company_recipient_emails(session, cert.company_id)

                # Trigger email
                for email in emails:
                    subject = f"ALERTA: Certificado digital a vencer en {days_left} días"
                    html = f"""
                    <html><body>
                        <h2>Alerta de Vencimiento de Certificado</h2>
                        <p>El certificado digital con CN <strong>{cert.common_name}</strong> está próximo a vencer.</p>
                        <ul>
                            <li><strong>Días restantes:</strong> {days_left} días</li>
                            <li><strong>Fecha de vencimiento:</strong> {cert.valid_until.strftime("%Y-%m-%d %H:%M:%S")}</li>
                            <li><strong>Número de serie:</strong> {cert.serial_number}</li>
                        </ul>
                        <p>Por favor, renueve su certificado antes de la fecha de vencimiento para evitar interrupciones con el SII.</p>
                    </body></html>
                    """
                    email_service.send_simple_email(email, subject, html)

                # Trigger webhook
                webhook_payload = {
                    "company_id": str(cert.company_id),
                    "certificate_id": str(cert.id),
                    "common_name": cert.common_name,
                    "serial_number": cert.serial_number,
                    "valid_until": cert.valid_until.isoformat(),
                    "days_left": days_left,
                }
                await dispatch_company_webhook(
                    session, cert.company_id, "certificate.expiring", webhook_payload
                )

                logger.info(
                    f"Certificate expiry alert sent: cert={cert.id} company={cert.company_id} days_left={days_left}"
                )
                alerts_triggered += 1

        return {"alerts_triggered": alerts_triggered}

    return _run_async(_check())


@celery_app.task(name="app.workers.tasks.alert_tasks.check_depleted_cafs_task", bind=True)
def check_depleted_cafs_task(self):
    """Daily check for CAF files that have used 80% or more of their folio range."""

    async def _check():
        from sqlalchemy import select

        from app.db.session import AsyncSessionLocal
        from app.models.caf_file import CAFFile
        from app.models.company import Company
        from app.modules.notifications.services.email_service import EmailService

        alerts_triggered = 0

        async with AsyncSessionLocal() as session:
            # Query CAFs for active companies
            result = await session.execute(
                select(CAFFile)
                .join(Company, Company.id == CAFFile.company_id)
                .where(Company.is_active == True)
            )
            cafs = result.scalars().all()

            email_service = EmailService()

            for caf in cafs:
                # Calculate consumption
                total_folios = caf.folio_to - caf.folio_from + 1
                curr_folio = caf.current_folio if caf.current_folio is not None else caf.folio_from
                used_folios = curr_folio - caf.folio_from

                pct_used = (used_folios / total_folios * 100.0) if total_folios > 0 else 0

                if pct_used >= 80.0:
                    # Calculate remaining folios
                    remaining = total_folios - used_folios

                    # Fetch users to notify
                    emails = await get_company_recipient_emails(session, caf.company_id)

                    # Trigger email
                    for email in emails:
                        subject = (
                            f"ALERTA: Folios CAF tipo {caf.dte_type} agotados al {pct_used:.1f}%"
                        )
                        html = f"""
                        <html><body>
                            <h2>Alerta de Consumo de Folios CAF</h2>
                            <p>Los folios para el documento tipo <strong>{caf.dte_type}</strong> están próximos a agotarse.</p>
                            <ul>
                                <li><strong>Porcentaje consumido:</strong> {pct_used:.1f}%</li>
                                <li><strong>Folios restantes:</strong> {remaining} (de {total_folios} totales)</li>
                                <li><strong>Rango autorizado:</strong> {caf.folio_from} - {caf.folio_to}</li>
                                <li><strong>Próximo folio a usar:</strong> {curr_folio}</li>
                            </ul>
                            <p>Por favor, cargue un nuevo archivo CAF para evitar bloqueos en la emisión de DTEs.</p>
                        </body></html>
                        """
                        email_service.send_simple_email(email, subject, html)

                    # Trigger webhook
                    webhook_payload = {
                        "company_id": str(caf.company_id),
                        "caf_file_id": str(caf.id),
                        "dte_type": caf.dte_type,
                        "folio_from": caf.folio_from,
                        "folio_to": caf.folio_to,
                        "current_folio": curr_folio,
                        "used_folios": used_folios,
                        "total_folios": total_folios,
                        "percentage_used": pct_used,
                        "remaining_folios": remaining,
                    }
                    await dispatch_company_webhook(
                        session, caf.company_id, "caf.depleted", webhook_payload
                    )

                    logger.info(
                        f"CAF depletion alert sent: caf={caf.id} company={caf.company_id} pct_used={pct_used:.1f}%"
                    )
                    alerts_triggered += 1

        return {"alerts_triggered": alerts_triggered}

    return _run_async(_check())
