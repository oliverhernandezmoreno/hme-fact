from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUserDep, SessionDep, TenantDep
from app.modules.apikeys.services.api_key_service import APIKeyService, APIKeyServiceError

router = APIRouter()


class CreateAPIKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    scopes: list[str] | None = None
    expires_in_days: int | None = Field(None, ge=1, le=365)


class APIKeyOut(BaseModel):
    id: uuid.UUID
    name: str
    prefix: str
    scopes: list[str]
    expires_at: str | None
    last_used_at: str | None
    is_active: bool
    created_at: str


@router.get("", summary="List active API Keys for company")
async def list_api_keys(
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = APIKeyService(session)
    keys = await svc.list_active(company_id)
    return [
        {
            "id": str(k.id),
            "name": k.name,
            "prefix": k.prefix,
            "scopes": k.scopes,
            "expires_at": k.expires_at.isoformat() if k.expires_at else None,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            "is_active": k.is_active,
            "created_at": k.created_at.isoformat(),
        }
        for k in keys
    ]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Generate a new API Key")
async def create_api_key(
    body: CreateAPIKeyRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = APIKeyService(session)
    try:
        result = await svc.generate(
            company_id=company_id,
            name=body.name,
            created_by_user_id=current_user.id,
            scopes=body.scopes,
            expires_in_days=body.expires_in_days,
        )
    except APIKeyServiceError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return {
        "id": str(result.api_key.id),
        "name": result.api_key.name,
        "prefix": result.api_key.prefix,
        "scopes": result.api_key.scopes,
        "raw_key": result.raw_key,  # Shown only once!
        "expires_at": result.api_key.expires_at.isoformat() if result.api_key.expires_at else None,
        "warning": "Store this key securely — it will not be shown again.",
    }


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke an API Key")
async def revoke_api_key(
    api_key_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = APIKeyService(session)
    try:
        await svc.revoke(api_key_id, company_id)
    except APIKeyServiceError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/{api_key_id}/rotate", summary="Rotate an API Key (revoke old, create new)")
async def rotate_api_key(
    api_key_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = APIKeyService(session)
    try:
        result = await svc.rotate(api_key_id, company_id, current_user.id)
    except APIKeyServiceError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return {
        "id": str(result.api_key.id),
        "name": result.api_key.name,
        "prefix": result.api_key.prefix,
        "raw_key": result.raw_key,
        "warning": "Store this key securely — it will not be shown again.",
    }
