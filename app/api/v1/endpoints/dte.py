from __future__ import annotations

import logging
import uuid
from typing import Any

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
from app.schemas.dte import DTECreate, DTERead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=list[DTERead])
async def list_dtes(
    session: SessionDep,
    company_id: TenantDep,
    offset: int = 0,
    limit: int = 100,
) -> list[DTERead]:
    """Listar DTEs para la empresa activa"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.models.dte import DTE

    stmt = (
        select(DTE)
        .where(DTE.company_id == company_id)
        .options(selectinload(DTE.items))
        .order_by(DTE.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    dtes = result.scalars().all()
    return [DTERead.model_validate(dte) for dte in dtes]


@router.post("", response_model=DTERead, status_code=status.HTTP_201_CREATED)
async def create_dte(
    payload: DTECreate,
    session: SessionDep,
    company_id: TenantDep,
) -> DTERead:
    """Crear un borrador de DTE y asignar folio desde el CAF correspondiente"""
    from decimal import Decimal

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.models.caf_file import CAFFile
    from app.models.certificate import Certificate
    from app.models.dte import DTE
    from app.models.dte_item import DTEItem

    # 1. Buscar CAF disponible para el tipo de DTE y empresa
    caf_stmt = (
        select(CAFFile)
        .where(
            CAFFile.company_id == company_id,
            CAFFile.dte_type == payload.dte_type,
            CAFFile.current_folio <= CAFFile.folio_to,
        )
        .order_by(CAFFile.authorization_date.desc(), CAFFile.folio_from.asc())
    )

    caf_result = await session.execute(caf_stmt)
    caf_file = caf_result.scalar_one_or_none()

    if not caf_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No hay folios disponibles para el tipo de documento {payload.dte_type}. "
                "Por favor, suba un archivo CAF válido."
            ),
        )

    folio = caf_file.current_folio
    caf_file.current_folio += 1

    # 2. Buscar certificado digital activo para la empresa si existe
    cert_stmt = select(Certificate).where(
        Certificate.company_id == company_id, Certificate.is_active
    )
    cert_result = await session.execute(cert_stmt)
    certificate = cert_result.scalar_one_or_none()
    certificate_id = certificate.id if certificate else None

    # 3. Calcular montos netos y exentos
    net_amount = Decimal("0.00")
    exempt_amount = Decimal("0.00")

    for item in payload.items:
        item_net = item.quantity * item.unit_price - item.discount_amount
        if item.tax_exempt:
            exempt_amount += item_net
        else:
            net_amount += item_net

    # Redondear a enteros para el estándar de facturación chilena
    net_amount = net_amount.quantize(Decimal("1."))
    exempt_amount = exempt_amount.quantize(Decimal("1."))
    tax_amount = (net_amount * Decimal("0.19")).quantize(Decimal("1."))
    total_amount = net_amount + exempt_amount + tax_amount

    # 4. Crear DTE
    dte = DTE(
        company_id=company_id,
        customer_id=payload.customer_id,
        certificate_id=certificate_id,
        caf_file_id=caf_file.id,
        dte_type=payload.dte_type,
        folio=folio,
        status=DTEStatus.DRAFT,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        net_amount=net_amount,
        exempt_amount=exempt_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        reference_dte_type=payload.reference_dte_type,
        reference_folio=payload.reference_folio,
        reference_date=payload.reference_date,
        reference_code=payload.reference_code,
        reference_reason=payload.reference_reason,
    )
    session.add(dte)
    await session.flush()  # Obtener ID del DTE

    # 5. Crear items del DTE
    for idx, item in enumerate(payload.items, start=1):
        item_net = (item.quantity * item.unit_price - item.discount_amount).quantize(Decimal("1."))
        item_tax = (
            Decimal("0.00")
            if item.tax_exempt
            else (item_net * Decimal("0.19")).quantize(Decimal("1."))
        )
        item_total = item_net + item_tax

        dte_item = DTEItem(
            dte_id=dte.id,
            product_id=item.product_id,
            line_number=idx,
            description=item.description,
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            discount_amount=item.discount_amount,
            net_amount=item_net,
            tax_amount=item_tax,
            total_amount=item_total,
            tax_exempt=item.tax_exempt,
        )
        session.add(dte_item)

    await session.commit()

    # Re-obtener con items precargados
    stmt = select(DTE).where(DTE.id == dte.id).options(selectinload(DTE.items))
    res = await session.execute(stmt)
    db_dte = res.scalar_one()
    return DTERead.model_validate(db_dte)


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
    from app.models import DTE
    from app.workers.tasks.dte_emission import emit_dte_task

    dte = await session.get(DTE, dte_id)
    if not dte or dte.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DTE not found")

    if dte.status != DTEStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"DTE debe estar en estado DRAFT para emitirse. Estado actual: {dte.status}",
        )

    # El cambio a "QUEUED" previene que se emita dos veces mientras Celery lo toma
    dte.status = DTEStatus.QUEUED
    await session.commit()

    # Disparar Job
    emit_dte_task.delay(str(dte_id))

    return {"message": "DTE queued for native emission to SII successfully", "status": "QUEUED"}


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
        from fastapi.responses import StreamingResponse

        file_stream = storage.get_file_stream(path)
        return StreamingResponse(
            file_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=dte_{dte.folio}.pdf"},
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PDF not generated yet"
        ) from exc


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
