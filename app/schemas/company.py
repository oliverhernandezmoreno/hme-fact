from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CompanyBase(BaseModel):
    rut: str = Field(max_length=12)
    legal_name: str = Field(max_length=255)
    fantasy_name: str | None = Field(default=None, max_length=255)
    giro: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    comuna: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    sii_resolution_number: int | None = None
    sii_resolution_date: date | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    legal_name: str | None = Field(default=None, max_length=255)
    fantasy_name: str | None = Field(default=None, max_length=255)
    giro: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    comuna: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    sii_resolution_number: int | None = None
    sii_resolution_date: date | None = None
    is_active: bool | None = None


class CompanyRead(CompanyBase, ORMModel):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
