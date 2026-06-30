from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update

from app.models.api_key import APIKey, APIUsageLog
from app.repositories.base import BaseRepository


class APIKeyRepository(BaseRepository[APIKey]):
    model = APIKey

    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode()).hexdigest()

    @staticmethod
    def generate_key_pair() -> tuple[str, str, str]:
        """Returns (prefix, raw_key, hashed_key)."""
        prefix = secrets.token_urlsafe(6)[:8]
        secret = secrets.token_urlsafe(32)
        raw_key = f"{prefix}.{secret}"
        hashed = hashlib.sha256(raw_key.encode()).hexdigest()
        return prefix, raw_key, hashed

    async def get_by_prefix_and_hash(self, raw_key: str) -> APIKey | None:
        """Validates a raw API key and returns the APIKey record if valid."""
        parts = raw_key.split(".", 1)
        if len(parts) != 2:
            return None
        prefix = parts[0]
        hashed = self.hash_key(raw_key)
        result = await self.session.scalars(
            select(APIKey).where(
                APIKey.prefix == prefix,
                APIKey.hashed_key == hashed,
                APIKey.is_active,
                APIKey.revoked_at is None,
            )
        )
        return result.first()

    async def get_active_by_company(self, company_id: uuid.UUID) -> list[APIKey]:
        result = await self.session.scalars(
            select(APIKey).where(
                APIKey.company_id == company_id,
                APIKey.is_active,
                APIKey.revoked_at is None,
            )
        )
        return list(result)

    async def revoke(self, api_key_id: uuid.UUID) -> None:
        now = datetime.now(UTC)
        await self.session.execute(
            update(APIKey).where(APIKey.id == api_key_id).values(revoked_at=now, is_active=False)
        )
        await self.session.commit()

    async def touch_last_used(self, api_key_id: uuid.UUID) -> None:
        await self.session.execute(
            update(APIKey).where(APIKey.id == api_key_id).values(last_used_at=datetime.now(UTC))
        )
        await self.session.commit()


class APIUsageLogRepository(BaseRepository[APIUsageLog]):
    model = APIUsageLog

    async def record(
        self,
        *,
        company_id: uuid.UUID,
        api_key_id: uuid.UUID | None,
        endpoint: str,
        method: str,
        status_code: int,
        processing_time_ms: int = 0,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> APIUsageLog:
        return await self.create(
            {
                "company_id": company_id,
                "api_key_id": api_key_id,
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "processing_time_ms": processing_time_ms,
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )
