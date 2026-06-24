from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.enums import DTEStatus
from app.schemas.common import ORMModel


class DTEItemBase(BaseModel):
    product_id: uuid.UUID | None = None
    description: str = Field(max_length=255)
    quantity: Decimal = Field(decimal_places=4, max_digits=14)
    unit: str = Field(default="UN", max_length=20)
    unit_price: Decimal = Field(decimal_places=2, max_digits=14)
    discount_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2, max_digits=14)
    tax_exempt: bool = False


class DTEItemCreate(DTEItemBase):
    pass


class DTEItemUpdate(BaseModel):
    product_id: uuid.UUID | None = None
    description: str | None = Field(default=None, max_length=255)
    quantity: Decimal | None = Field(default=None, decimal_places=4, max_digits=14)
    unit: str | None = Field(default=None, max_length=20)
    unit_price: Decimal | None = Field(default=None, decimal_places=2, max_digits=14)
    discount_amount: Decimal | None = Field(default=None, decimal_places=2, max_digits=14)
    tax_exempt: bool | None = None


class DTEItemRead(DTEItemBase, ORMModel):
    id: uuid.UUID
    dte_id: uuid.UUID
    line_number: int
    net_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime


class DTEBase(BaseModel):
    customer_id: uuid.UUID
    dte_type: int = Field(ge=33, le=61)
    issue_date: date
    due_date: date | None = None
    reference_dte_type: int | None = None
    reference_folio: int | None = None
    reference_date: date | None = None
    reference_code: int | None = None
    reference_reason: str | None = Field(default=None, max_length=90)


class DTECreate(DTEBase):
    items: list[DTEItemCreate] = Field(min_length=1)


class DTEUpdate(BaseModel):
    customer_id: uuid.UUID | None = None
    issue_date: date | None = None
    due_date: date | None = None
    reference_dte_type: int | None = None
    reference_folio: int | None = None
    reference_date: date | None = None
    reference_code: int | None = None
    reference_reason: str | None = Field(default=None, max_length=90)
    status: DTEStatus | None = None


class DTERead(DTEBase, ORMModel):
    id: uuid.UUID
    company_id: uuid.UUID
    folio: int
    status: DTEStatus
    net_amount: Decimal
    exempt_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    sii_track_id: str | None = None
    sent_at: datetime | None = None
    accepted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    items: list[DTEItemRead]
