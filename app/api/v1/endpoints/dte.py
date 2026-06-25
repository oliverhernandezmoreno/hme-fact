from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import SessionDep, TenantDep
from app.models import DTEStatus
from app.modules.integrations.exceptions import TaxIntegrationError
from app.modules.integrations.schemas.tax import DTEStatusResponse
from app.modules.integrations.services.tax_integration import (
    TaxIntegrationService,
    http_status_for_tax_error,
)
from app.modules.xml.services.xml_render_service import XmlRenderService
from app.modules.xml.validators.exceptions import XmlValidationError
from app.repositories.dte import DTERepository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/{dte_id}/generate-xml",
    response_class=Response,
    responses={200: {"content": {"application/xml": {}}}},
)
async def generate_dte_xml(
    dte_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> Response:
    dte = await DTERepository(session).get_with_xml_dependencies(
        dte_id=dte_id,
        company_id=company_id,
    )
    if dte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DTE not found")

    try:
        xml_content = await XmlRenderService(session).generate_and_store_dte_xml(dte)
        dte.status = DTEStatus.GENERATED
        await session.commit()
    except XmlValidationError as exc:
        logger.warning(
            "DTE XML validation failed",
            extra={"dte_id": str(dte_id), "errors": exc.errors},
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors,
        ) from exc

    return Response(content=xml_content, media_type="application/xml; charset=utf-8")


@router.post("/{dte_id}/send", response_model=DTEStatusResponse)
async def send_dte(
    dte_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> DTEStatusResponse:
    try:
        return await TaxIntegrationService(session).send_dte(
            dte_id=dte_id,
            company_id=company_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DTE not found") from exc
    except TaxIntegrationError as exc:
        logger.warning(
            "DTE tax integration send failed",
            extra={
                "dte_id": str(dte_id),
                "provider": exc.provider,
                "error_type": exc.__class__.__name__,
            },
        )
        raise HTTPException(
            status_code=http_status_for_tax_error(exc),
            detail={
                "message": exc.message,
                "provider": exc.provider,
                "retryable": exc.retryable,
                "payload": exc.payload,
            },
        ) from exc


@router.post(
    "/{dte_id}/emit",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Emitir DTE al SII usando el Motor Nativo (Fase 8)",
)
async def emit_dte_native(
    dte_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> dict[str, str]:
    from sqlalchemy import select
    from app.models import DTE
    from app.workers.tasks.dte_emission import emit_dte_task

    dte = await session.get(DTE, dte_id)
    if not dte or dte.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DTE not found")

    if dte.status != DTEStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"DTE debe estar en estado DRAFT para emitirse. Estado actual: {dte.status}"
        )

    # El cambio a "QUEUED" previene que se emita dos veces mientras Celery lo toma
    dte.status = DTEStatus.QUEUED
    await session.commit()

    # Disparar Job
    emit_dte_task.delay(str(dte_id))
    
    return {
        "message": "DTE queued for native emission to SII successfully",
        "status": "QUEUED"
    }


@router.get("/{dte_id}/status", response_model=DTEStatusResponse)
async def get_dte_status(
    dte_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> DTEStatusResponse:
    try:
        return await TaxIntegrationService(session).get_status(
            dte_id=dte_id,
            company_id=company_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DTE not found") from exc
    except TaxIntegrationError as exc:
        logger.warning(
            "DTE tax integration status failed",
            extra={
                "dte_id": str(dte_id),
                "provider": exc.provider,
                "error_type": exc.__class__.__name__,
            },
        )
        raise HTTPException(
            status_code=http_status_for_tax_error(exc),
            detail={
                "message": exc.message,
                "provider": exc.provider,
                "retryable": exc.retryable,
                "payload": exc.payload,
            },
        ) from exc


@router.post(
    "/{dte_id}/generate-pdf",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate PDF for DTE asynchronously",
)
async def generate_dte_pdf(
    dte_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> dict[str, str]:
    from app.workers.tasks.dte_tasks import generate_dte_pdf_task
    generate_dte_pdf_task.delay(str(dte_id), str(company_id))
    return {"message": "PDF generation queued successfully"}


@router.get(
    "/{dte_id}/pdf",
    summary="Download generated PDF",
)
async def get_dte_pdf(
    dte_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> Any:
    from fastapi.responses import Response
    from sqlalchemy import select
    from app.models import DTE
    from app.services.storage import get_file_storage_service

    result = await session.execute(
        select(DTE).where(DTE.id == dte_id, DTE.company_id == company_id)
    )
    dte = result.scalar_one_or_none()
    if not dte:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DTE not found")

    storage = get_file_storage_service()
    path = f"companies/{company_id}/dtes/{dte_id}/dte_{dte.folio}.pdf"
    
    try:
        pdf_content = await storage.get_file(path)
        return Response(content=pdf_content, media_type="application/pdf")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not generated yet")


@router.post(
    "/{dte_id}/send-email",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send DTE via email asynchronously",
)
async def send_dte_email(
    dte_id: uuid.UUID,
    to_email: str,
    session: SessionDep,
    company_id: TenantDep,
) -> dict[str, str]:
    from app.workers.tasks.dte_tasks import send_dte_email_task
    send_dte_email_task.delay(str(dte_id), str(company_id), to_email)
    return {"message": "Email sending queued successfully"}


@router.post(
    "/{dte_id}/retry",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry failed DTE transmission",
)
async def retry_dte(
    dte_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> dict[str, str]:
    from app.workers.tasks.dte_tasks import send_dte_task
    send_dte_task.delay(str(dte_id), str(company_id))
    return {"message": "DTE retry queued successfully"}


@router.get(
    "/{dte_id}/events",
    summary="Get event history of DTE",
)
async def get_dte_events(
    dte_id: uuid.UUID,
    session: SessionDep,
    company_id: TenantDep,
) -> Any:
    from sqlalchemy import select
    from app.models.audit_log import AuditLog
    
    result = await session.execute(
        select(AuditLog)
        .where(AuditLog.entity_id == dte_id, AuditLog.company_id == company_id)
        .order_by(AuditLog.created_at.desc())
    )
    return result.scalars().all()
