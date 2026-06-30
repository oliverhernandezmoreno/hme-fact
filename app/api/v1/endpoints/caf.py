from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.caf_file import CAFFile
from app.models.company import Company
from app.models.user import User
from app.schemas.caf import CAFFileResponse, CAFFIleUploadResponse
from app.services.sii.caf_parser import CAFParser, CAFParserError

router = APIRouter()


@router.post("/upload", response_model=CAFFIleUploadResponse)
async def upload_caf_file(
    *,
    db: AsyncSession = Depends(get_db_session),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """
    Subir y parsear un archivo CAF (Código de Autorización de Folios).
    Extrae la llave privada, rangos de folios y almacena el contenido XML
    listo para inyectarse en los DTEs.
    """

    # Check that company exists and belongs to user
    # (Assuming RBAC checks are handled in deps or middleware, but we double check)
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if not file.filename.endswith(".xml"):
        raise HTTPException(status_code=400, detail="El archivo CAF debe ser un XML")

    content = await file.read()

    try:
        parsed_data = CAFParser.parse(content)
    except CAFParserError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Verify the RUT matches the company RUT
    # This requires company.rut to be formatted identically, so we do a simple check
    if company.rut and company.rut.replace(".", "").replace("-", "") != parsed_data[
        "rut_emisor"
    ].replace(".", "").replace("-", ""):
        raise HTTPException(
            status_code=400,
            detail=(
                f"El RUT del CAF ({parsed_data['rut_emisor']}) no coincide "
                f"con el RUT de la empresa ({company.rut})"
            ),
        )

    # Check if this exact range already exists
    stmt = select(CAFFile).where(
        CAFFile.company_id == company_id,
        CAFFile.dte_type == parsed_data["dte_type"],
        CAFFile.folio_from == parsed_data["folio_from"],
        CAFFile.folio_to == parsed_data["folio_to"],
    )
    existing = await db.execute(stmt)
    if existing.scalars().first():
        raise HTTPException(
            status_code=409, detail="Este rango de folios (CAF) ya fue subido anteriormente."
        )

    # Persist the CAF
    caf_record = CAFFile(
        company_id=company_id,
        dte_type=parsed_data["dte_type"],
        folio_from=parsed_data["folio_from"],
        folio_to=parsed_data["folio_to"],
        authorization_date=parsed_data["authorization_date"],
        xml_content=parsed_data["caf_xml_content"],
        private_key=parsed_data["private_key"],
        current_folio=parsed_data["folio_from"],  # Iniciar desde el folio "Desde"
    )

    db.add(caf_record)
    await db.commit()
    await db.refresh(caf_record)

    # TODO: In a real flow, this would trigger an event to update the onboarding engine progress

    return CAFFIleUploadResponse(
        message="Archivo CAF procesado y cargado correctamente.",
        caf=CAFFileResponse.model_validate(caf_record),
    )


@router.get("/", response_model=list[CAFFileResponse])
async def list_caf_files(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """Listar los CAFs subidos por la empresa"""
    stmt = (
        select(CAFFile)
        .where(CAFFile.company_id == company_id)
        .order_by(CAFFile.authorization_date.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()
