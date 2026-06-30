from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import CurrentUserDep, SessionDep, TenantDep
from app.modules.rbac.services.rbac_service import RBACService

router = APIRouter()


class AssignRoleRequest(BaseModel):
    user_id: uuid.UUID
    role_name: str


@router.get("/roles", summary="List available system roles")
async def list_roles(session: SessionDep, current_user: CurrentUserDep):
    from app.repositories.rbac import RoleRepository

    repo = RoleRepository(session)
    roles = await repo.get_all_system()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "description": r.description,
            "scope": r.scope,
        }
        for r in roles
    ]


@router.get("/my-permissions", summary="Get current user permissions for company")
async def my_permissions(
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = RBACService(session)
    roles = await svc.get_user_roles(current_user.id, company_id)
    perms = await svc.get_user_permissions(current_user.id, company_id)
    return {
        "user_id": str(current_user.id),
        "company_id": str(company_id),
        "roles": [r.name for r in roles],
        "permissions": [{"module": m, "action": a, "resource": r} for m, a, r in sorted(perms)],
    }


@router.post(
    "/users/{user_id}/roles", status_code=status.HTTP_201_CREATED, summary="Assign role to user"
)
async def assign_role(
    user_id: uuid.UUID,
    body: AssignRoleRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = RBACService(session)
    try:
        await svc.assign_role(user_id, body.role_name, company_id)
        return {"message": f"Role '{body.role_name}' assigned to user {user_id}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/users/{user_id}/roles/{role_name}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role(
    user_id: uuid.UUID,
    role_name: str,
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = RBACService(session)
    try:
        await svc.remove_role(user_id, role_name, company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
