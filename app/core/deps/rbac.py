from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.deps import CurrentUserDep, SessionDep, TenantDep
from app.modules.rbac.services.rbac_service import RBACService


async def get_rbac_service(session: SessionDep) -> RBACService:
    return RBACService(session)


RBACServiceDep = Annotated[RBACService, Depends(get_rbac_service)]


def require_permission(module: str, action: str):
    """
    FastAPI dependency factory for permission-based authorization.
    Usage: Depends(require_permission("dte", "write"))
    Completely decoupled from JWT — resolves permissions from DB.
    """

    async def _check(
        current_user: CurrentUserDep,
        company_id: TenantDep,
        rbac: RBACServiceDep,
    ) -> None:
        allowed = await rbac.has_permission(current_user.id, company_id, module, action)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {module}:{action}",
            )

    return Depends(_check)


def require_super_admin():
    """Dependency that restricts access to SuperAdmin role only."""

    async def _check(
        current_user: CurrentUserDep,
        rbac: RBACServiceDep,
    ) -> None:
        is_admin = await rbac.is_super_admin(current_user.id)
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SuperAdmin access required",
            )

    return Depends(_check)


SuperAdminRequired = require_super_admin()
