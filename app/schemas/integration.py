from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IntegrationConnectionBase(BaseModel):
    provider: str
    is_active: bool = False
    credentials: dict[str, Any] = {}
    settings: dict[str, Any] = {}


class IntegrationConnectionCreate(IntegrationConnectionBase):
    pass


class IntegrationConnectionUpdate(BaseModel):
    is_active: bool | None = None
    credentials: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None


class IntegrationConnectionResponse(IntegrationConnectionBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WebhookSubscriptionBase(BaseModel):
    target_url: str
    event_types: list[str]
    is_active: bool = True


class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    pass


class WebhookSubscriptionUpdate(BaseModel):
    target_url: str | None = None
    event_types: list[str] | None = None
    is_active: bool | None = None


class WebhookSubscriptionResponse(WebhookSubscriptionBase):
    id: UUID
    company_id: UUID
    secret: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ExternalOrderPayload(BaseModel):
    idempotency_key: str
    source: str  # shopify, woocommerce, pos, erp
    external_order_id: str
    customer: dict[str, Any]
    items: list[dict[str, Any]]
    total_amount: float
    tax_amount: float
    net_amount: float
    metadata: dict[str, Any] = {}
