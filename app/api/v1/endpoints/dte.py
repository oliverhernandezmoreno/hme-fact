from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import SessionDep, TenantDep
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
