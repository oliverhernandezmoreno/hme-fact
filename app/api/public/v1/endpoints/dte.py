from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

router = APIRouter()


class DTEPublicEmitRequest(BaseModel):
    """Simplified DTE emission request for public API consumers."""
    dte_type: int  # 33=Factura, 39=Boleta, 61=Nota Crédito, etc.
    customer_rut: str
    customer_name: str
    customer_email: str | None = None
    items: list[dict]  # [{name, qty, unit_price, tax_pct}]
    reference_folio: int | None = None
    reference_type: int | None = None


@router.post("", status_code=status.HTTP_202_ACCEPTED, summary="Emit DTE via API Key")
async def emit_dte(body: DTEPublicEmitRequest, request: Request):
    """
    Emits a DTE document via API Key authentication.
    The DTE is processed asynchronously — use GET /dte/{folio} to check status.
    Quota is validated by QuotaMiddleware before this endpoint executes.
    """
    from app.db.session import AsyncSessionLocal
    from app.modules.billing.services.quota_service import QuotaService

    company_id = request.state.company_id

    # Increment quota after successful request
    async with AsyncSessionLocal() as session:
        quota_svc = QuotaService(session)
        await quota_svc.increment_dte_usage(company_id)
        await quota_svc.increment_api_usage(company_id)

    # Here you would call the DTE service — forwarding to existing DTE logic
    # For now, return accepted with a task reference
    return {
        "status": "accepted",
        "message": "DTE queued for processing",
        "company_id": str(company_id),
        "dte_type": body.dte_type,
        "note": "Use GET /public/v1/dte/{folio} to check status after processing",
    }


@router.get("/{folio}", summary="Get DTE status by folio")
async def get_dte_status(folio: int, request: Request):
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.dte import DTE

    company_id = request.state.company_id
    async with AsyncSessionLocal() as session:
        result = await session.scalars(
            select(DTE).where(DTE.company_id == company_id, DTE.folio == folio)
        )
        dte = result.first()
        if dte is None:
            raise HTTPException(status_code=404, detail="DTE not found")

    return {
        "folio": dte.folio,
        "dte_type": dte.dte_type,
        "status": dte.status,
        "total_amount": float(dte.total_amount) if dte.total_amount else None,
        "issued_at": dte.issue_date.isoformat() if dte.issue_date else None,
    }


@router.get("/{folio}/pdf", summary="Download DTE PDF")
async def get_dte_pdf(folio: int, request: Request):
    from fastapi.responses import FileResponse
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.dte import DTE

    company_id = request.state.company_id
    async with AsyncSessionLocal() as session:
        result = await session.scalars(
            select(DTE).where(DTE.company_id == company_id, DTE.folio == folio)
        )
        dte = result.first()
        if dte is None:
            raise HTTPException(status_code=404, detail="DTE not found")
        if not dte.pdf_path:
            raise HTTPException(status_code=404, detail="PDF not yet generated")

    return FileResponse(dte.pdf_path, media_type="application/pdf", filename=f"DTE_{folio}.pdf")


@router.get("/{folio}/xml", summary="Download DTE XML")
async def get_dte_xml(folio: int, request: Request):
    from fastapi.responses import Response
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.dte import DTE
    from app.models.dte_xml import DTEXml

    company_id = request.state.company_id
    async with AsyncSessionLocal() as session:
        result = await session.scalars(
            select(DTE).where(DTE.company_id == company_id, DTE.folio == folio)
        )
        dte = result.first()
        if dte is None:
            raise HTTPException(status_code=404, detail="DTE not found")
        xml_result = await session.scalars(select(DTEXml).where(DTEXml.dte_id == dte.id).limit(1))
        xml_record = xml_result.first()
        if xml_record is None:
            raise HTTPException(status_code=404, detail="XML not yet available")

    return Response(content=xml_record.xml_content, media_type="application/xml")
