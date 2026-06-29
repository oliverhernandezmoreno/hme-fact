import secrets
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration import IntegrationConnection, WebhookSubscription
from app.schemas.integration import (
    IntegrationConnectionCreate,
    IntegrationConnectionUpdate,
    WebhookSubscriptionCreate,
)


class CRUDIntegrationConnection:
    async def get(self, db: AsyncSession, id: UUID) -> IntegrationConnection | None:
        result = await db.execute(
            select(IntegrationConnection).filter(IntegrationConnection.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_company(
        self, db: AsyncSession, company_id: UUID
    ) -> list[IntegrationConnection]:
        result = await db.execute(
            select(IntegrationConnection).filter(IntegrationConnection.company_id == company_id)
        )
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, *, obj_in: IntegrationConnectionCreate, company_id: UUID
    ) -> IntegrationConnection:
        db_obj = IntegrationConnection(
            company_id=company_id,
            provider=obj_in.provider,
            is_active=obj_in.is_active,
            credentials=obj_in.credentials,
            settings=obj_in.settings,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: IntegrationConnection,
        obj_in: IntegrationConnectionUpdate,
    ) -> IntegrationConnection:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


class CRUDWebhookSubscription:
    async def get_by_company(self, db: AsyncSession, company_id: UUID) -> list[WebhookSubscription]:
        result = await db.execute(
            select(WebhookSubscription).filter(WebhookSubscription.company_id == company_id)
        )
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, *, obj_in: WebhookSubscriptionCreate, company_id: UUID
    ) -> WebhookSubscription:
        secret = secrets.token_urlsafe(32)
        db_obj = WebhookSubscription(
            company_id=company_id,
            target_url=obj_in.target_url,
            event_types=obj_in.event_types,
            secret=secret,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


integration_connection = CRUDIntegrationConnection()
webhook_subscription = CRUDWebhookSubscription()
