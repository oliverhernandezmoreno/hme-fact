from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import SessionDep, TenantDep
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get all audit logs for the current company",
)
async def get_audit_logs(
    session: SessionDep,
    tenant: TenantDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    result = await session.execute(
        select(AuditLog)
        .where(AuditLog.company_id == tenant.id)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
