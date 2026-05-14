from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ProductBase(BaseModel):
    sku: str | None = Field(default=None, max_length=64)
    name: str = Field(max_length=255)
    description: str | None = None
    unit: str = Field(default="UN", max_length=20)
    unit_price: Decimal = Field(decimal_places=2, max_digits=14)
    tax_exempt: bool = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, max_length=64)
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    unit: str | None = Field(default=None, max_length=20)
    unit_price: Decimal | None = Field(default=None, decimal_places=2, max_digits=14)
    tax_exempt: bool | None = None
    is_active: bool | None = None


class ProductRead(ProductBase, ORMModel):
    id: uuid.UUID
    company_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
