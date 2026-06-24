from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DTEStatus


class TaxProviderContext(BaseModel):
    company_id: uuid.UUID
    dte_id: uuid.UUID
    company_rut: str
    dte_type: int
    folio: int


class TaxSendRequest(BaseModel):
    xml_content: str
    context: TaxProviderContext


class TaxProviderErrorDetail(BaseModel):
    code: str | None = None
    message: str
    field: str | None = None
    raw: dict[str, Any] | None = None


class TaxProviderStatus(BaseModel):
    status: DTEStatus
    provider_status: str
    track_id: str | None = None
    detail: str | None = None
    errors: list[TaxProviderErrorDetail] = Field(default_factory=list)


class TaxProviderResponse(TaxProviderStatus):
    provider: str
    raw_response: dict[str, Any] = Field(default_factory=dict)
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    duration_ms: int | None = None


class ProviderHealthResponse(BaseModel):
    provider: str
    ok: bool
    raw_response: dict[str, Any] = Field(default_factory=dict)


class CompanyInfoResponse(BaseModel):
    provider: str
    rut: str
    legal_name: str | None = None
    giro: str | None = None
    raw_response: dict[str, Any] = Field(default_factory=dict)


class DTETransmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dte_id: uuid.UUID
    provider: str
    external_track_id: str | None
    status: str
    sent_at: datetime | None
    last_check_at: datetime | None


class DTEStatusResponse(BaseModel):
    dte_id: uuid.UUID
    status: DTEStatus
    provider: str
    external_track_id: str | None = None
    provider_status: str | None = None
    detail: str | None = None
    errors: list[TaxProviderErrorDetail] = Field(default_factory=list)
    transmission: DTETransmissionRead | None = None
