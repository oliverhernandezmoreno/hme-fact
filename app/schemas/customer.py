from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class CustomerBase(BaseModel):
    rut: str = Field(max_length=12)
    legal_name: str = Field(max_length=255)
    giro: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    comuna: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    legal_name: str | None = Field(default=None, max_length=255)
    giro: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    comuna: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class CustomerRead(CustomerBase, ORMModel):
    id: uuid.UUID
    company_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
