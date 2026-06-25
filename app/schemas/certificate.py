from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CertificateBase(BaseModel):
    common_name: str = Field(max_length=255)
    serial_number: str = Field(max_length=128)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool = True


class CertificateCreate(CertificateBase):
    encrypted_pfx: bytes
    encrypted_password: bytes | None = None


class CertificateUpdate(BaseModel):
    is_active: bool | None = None


class CertificateResponse(CertificateBase, ORMModel):
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
