from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.api_key import APIKeyRepository, APIUsageLogRepository
from app.models.api_key import APIKey


@dataclass
class GeneratedAPIKey:
    api_key: APIKey
    raw_key: str  # Shown only once at generation time


class APIKeyServiceError(Exception):
    pass


class APIKeyService:
    VALID_SCOPES = {"read", "write", "dte", "customers", "products"}

    def __init__(self, session: AsyncSession) -> None:
        self._repo = APIKeyRepository(session)
        self._log_repo = APIUsageLogRepository(session)

    async def generate(
        self,
        *,
        company_id: uuid.UUID,
        name: str,
        created_by_user_id: uuid.UUID,
        scopes: list[str] | None = None,
        expires_in_days: int | None = None,
    ) -> GeneratedAPIKey:
        if scopes:
            invalid = set(scopes) - self.VALID_SCOPES
            if invalid:
                raise APIKeyServiceError(f"Invalid scopes: {invalid}")

        prefix, raw_key, hashed = self._repo.generate_key_pair()
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        api_key = await self._repo.create({
            "company_id": company_id,
            "created_by_user_id": created_by_user_id,
            "name": name,
            "prefix": prefix,
            "hashed_key": hashed,
            "scopes": scopes or list(self.VALID_SCOPES),
            "expires_at": expires_at,
            "is_active": True,
        })
        return GeneratedAPIKey(api_key=api_key, raw_key=raw_key)

    async def validate(self, raw_key: str) -> APIKey | None:
        api_key = await self._repo.get_by_prefix_and_hash(raw_key)
        if api_key is None:
            return None
        if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
            return None
        await self._repo.touch_last_used(api_key.id)
        return api_key

    async def revoke(self, api_key_id: uuid.UUID, company_id: uuid.UUID) -> None:
        key = await self._repo.get(api_key_id)
        if key is None or key.company_id != company_id:
            raise APIKeyServiceError("API Key not found or access denied")
        await self._repo.revoke(api_key_id)

    async def rotate(
        self, api_key_id: uuid.UUID, company_id: uuid.UUID, created_by_user_id: uuid.UUID
    ) -> GeneratedAPIKey:
        old_key = await self._repo.get(api_key_id)
        if old_key is None or old_key.company_id != company_id:
            raise APIKeyServiceError("API Key not found or access denied")
        await self._repo.revoke(api_key_id)
        return await self.generate(
            company_id=company_id,
            name=f"{old_key.name} (rotated)",
            created_by_user_id=created_by_user_id,
            scopes=old_key.scopes,
        )

    async def list_active(self, company_id: uuid.UUID) -> list[APIKey]:
        return await self._repo.get_active_by_company(company_id)

    async def record_usage(
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
    ) -> None:
        await self._log_repo.record(
            company_id=company_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            processing_time_ms=processing_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
        )
