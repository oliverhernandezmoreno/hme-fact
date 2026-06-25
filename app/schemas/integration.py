from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IntegrationConnectionBase(BaseModel):
    provider: str
    is_active: bool = False
    credentials: Dict[str, Any] = {}
    settings: Dict[str, Any] = {}


class IntegrationConnectionCreate(IntegrationConnectionBase):
    pass


class IntegrationConnectionUpdate(BaseModel):
    is_active: Optional[bool] = None
    credentials: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class IntegrationConnectionResponse(IntegrationConnectionBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WebhookSubscriptionBase(BaseModel):
    target_url: str
    event_types: List[str]
    is_active: bool = True


class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    pass


class WebhookSubscriptionUpdate(BaseModel):
    target_url: Optional[str] = None
    event_types: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WebhookSubscriptionResponse(WebhookSubscriptionBase):
    id: UUID
    company_id: UUID
    secret: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ExternalOrderPayload(BaseModel):
    idempotency_key: str
    source: str # shopify, woocommerce, pos, erp
    external_order_id: str
    customer: Dict[str, Any]
    items: List[Dict[str, Any]]
    total_amount: float
    tax_amount: float
    net_amount: float
    metadata: Dict[str, Any] = {}
