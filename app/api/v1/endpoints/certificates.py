from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.crud.crud_certificate import certificate as crud_certificate
from app.models.user import User
from app.schemas.certificate import CertificateCreate, CertificateResponse
from app.services.certificate_security import CertificateSecurityService

router = APIRouter()
security_service = CertificateSecurityService()


@router.get("/", response_model=list[CertificateResponse])
async def list_certificates(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """List all digital certificates for the active company."""
    return await crud_certificate.get_by_company(db, company_id=company_id)


@router.post("/upload", response_model=CertificateResponse)
async def upload_certificate(
    file: UploadFile = File(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """
    Upload a digital certificate (.p12 or .pfx), extract metadata,
    and store it securely in the database.
    """
    if not file.filename.endswith((".p12", ".pfx")):
        raise HTTPException(status_code=400, detail="Only .p12 and .pfx files are supported")

    # Read binary content
    pfx_data = await file.read()

    # 1. Extract Metadata and Validate Password
    try:
        metadata = security_service.extract_metadata(pfx_data, password)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid certificate or incorrect password: {str(e)}"
        )

    # 2. Encrypt sensitive data before storing
    encrypted_pfx = security_service.encrypt_data(pfx_data)
    encrypted_password = security_service.encrypt_data(password.encode("utf-8"))

    # 3. Mark previous certificates as inactive
    await crud_certificate.deactivate_all_for_company(db, company_id)

    # 4. Save new certificate in Database
    cert_create = CertificateCreate(
        common_name=metadata["common_name"],
        serial_number=metadata["serial_number"],
        valid_from=metadata["valid_from"],
        valid_until=metadata["valid_until"],
        encrypted_pfx=encrypted_pfx,
        encrypted_password=encrypted_password,
        is_active=True,
    )

    cert = await crud_certificate.create(db, obj_in=cert_create, company_id=company_id)
    return cert
