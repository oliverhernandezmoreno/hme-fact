from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.crud.crud_integration import integration_connection, webhook_subscription
from app.models.user import User
from app.schemas.integration import (
    IntegrationConnectionCreate,
    IntegrationConnectionResponse,
    IntegrationConnectionUpdate,
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
)

router = APIRouter()


@router.get("/connections", response_model=list[IntegrationConnectionResponse])
async def list_connections(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """List all integrations configured for the active company."""
    return await integration_connection.get_by_company(db, company_id=company_id)


@router.post("/connections", response_model=IntegrationConnectionResponse)
async def create_connection(
    *,
    db: AsyncSession = Depends(get_db_session),
    obj_in: IntegrationConnectionCreate,
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """Configure a new integration connection."""
    return await integration_connection.create(db, obj_in=obj_in, company_id=company_id)


@router.patch("/connections/{id}", response_model=IntegrationConnectionResponse)
async def update_connection(
    *,
    db: AsyncSession = Depends(get_db_session),
    id: UUID,
    obj_in: IntegrationConnectionUpdate,
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """Update an integration connection."""
    conn = await integration_connection.get(db, id=id)
    if not conn or conn.company_id != company_id:
        raise HTTPException(status_code=404, detail="Integration not found")
    return await integration_connection.update(db, db_obj=conn, obj_in=obj_in)


@router.get("/webhooks", response_model=list[WebhookSubscriptionResponse])
async def list_webhooks(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """List webhook subscriptions."""
    return await webhook_subscription.get_by_company(db, company_id=company_id)


@router.post("/webhooks", response_model=WebhookSubscriptionResponse)
async def create_webhook(
    *,
    db: AsyncSession = Depends(get_db_session),
    obj_in: WebhookSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """Create a webhook subscription."""
    return await webhook_subscription.create(db, obj_in=obj_in, company_id=company_id)
