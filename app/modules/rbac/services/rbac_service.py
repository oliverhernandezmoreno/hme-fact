from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rbac import Role
from app.repositories.rbac import PermissionRepository, RoleRepository, UserRoleRepository


@dataclass
class PermissionDef:
    module: str
    action: str
    resource: str


# System roles with their permissions
SYSTEM_ROLES: dict[str, dict] = {
    "SuperAdmin": {
        "description": "Full platform control",
        "scope": "platform",
        "permissions": [],  # SuperAdmin bypasses all checks
    },
    "CompanyOwner": {
        "description": "Company owner — full company access",
        "scope": "company",
        "permissions": [
            ("companies", "read", "*"),
            ("companies", "write", "*"),
            ("users", "read", "*"),
            ("users", "write", "*"),
            ("dte", "read", "*"),
            ("dte", "write", "*"),
            ("customers", "read", "*"),
            ("customers", "write", "*"),
            ("products", "read", "*"),
            ("products", "write", "*"),
            ("billing", "read", "*"),
            ("billing", "write", "*"),
            ("api_keys", "read", "*"),
            ("api_keys", "write", "*"),
            ("reports", "read", "*"),
        ],
    },
    "Accountant": {
        "description": "Full DTE + customer access, read billing",
        "scope": "company",
        "permissions": [
            ("dte", "read", "*"),
            ("dte", "write", "*"),
            ("customers", "read", "*"),
            ("customers", "write", "*"),
            ("products", "read", "*"),
            ("products", "write", "*"),
            ("billing", "read", "*"),
            ("reports", "read", "*"),
        ],
    },
    "Seller": {
        "description": "DTE emission only",
        "scope": "company",
        "permissions": [
            ("dte", "write", "create"),
            ("dte", "read", "*"),
            ("customers", "read", "*"),
            ("products", "read", "*"),
        ],
    },
    "Viewer": {
        "description": "Read-only access",
        "scope": "company",
        "permissions": [
            ("dte", "read", "*"),
            ("customers", "read", "*"),
            ("products", "read", "*"),
            ("billing", "read", "*"),
            ("reports", "read", "*"),
        ],
    },
    "APIUser": {
        "description": "Authenticated via API Key only",
        "scope": "company",
        "permissions": [
            ("dte", "write", "create"),
            ("dte", "read", "*"),
            ("customers", "read", "*"),
            ("customers", "write", "*"),
            ("products", "read", "*"),
        ],
    },
}


class RBACService:
    def __init__(self, session: AsyncSession) -> None:
        self._role_repo = RoleRepository(session)
        self._perm_repo = PermissionRepository(session)
        self._user_role_repo = UserRoleRepository(session)

    async def seed_default_roles(self) -> None:
        for role_name, cfg in SYSTEM_ROLES.items():
            role = await self._role_repo.get_by_name(role_name)
            if role is None:
                role = await self._role_repo.create(
                    {
                        "name": role_name,
                        "description": cfg["description"],
                        "scope": cfg["scope"],
                        "is_system": True,
                    }
                )

            for module, action, resource in cfg.get("permissions", []):
                perm = await self._perm_repo.get_by_module_action(module, action, resource)
                if perm is None:
                    perm = await self._perm_repo.create(
                        {
                            "module": module,
                            "action": action,
                            "resource": resource,
                        }
                    )
                sql = (
                    "INSERT INTO role_permissions "
                    "(id, role_id, permission_id, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), :r, :p, now(), now()) "
                    "ON CONFLICT DO NOTHING"
                )
                await self._user_role_repo.session.execute(
                    __import__("sqlalchemy", fromlist=["text"]).text(sql),
                    {"r": str(role.id), "p": str(perm.id)},
                )
        await self._user_role_repo.session.commit()

    async def get_user_permissions(
        self, user_id: uuid.UUID, company_id: uuid.UUID | None = None
    ) -> set[tuple[str, str, str]]:
        return await self._user_role_repo.get_user_permissions(user_id, company_id)

    async def has_permission(
        self,
        user_id: uuid.UUID,
        company_id: uuid.UUID | None,
        module: str,
        action: str,
    ) -> bool:
        # SuperAdmin always passes
        if await self._user_role_repo.has_role(user_id, "SuperAdmin"):
            return True
        perms = await self.get_user_permissions(user_id, company_id)
        return (
            (module, action, "*") in perms
            or (module, action, action) in perms
            or (module, "*", "*") in perms
        )

    async def is_super_admin(self, user_id: uuid.UUID) -> bool:
        return await self._user_role_repo.has_role(user_id, "SuperAdmin")

    async def assign_role(
        self,
        user_id: uuid.UUID,
        role_name: str,
        company_id: uuid.UUID | None = None,
    ) -> None:
        role = await self._role_repo.get_by_name(role_name)
        if role is None:
            raise ValueError(f"Role '{role_name}' not found")
        await self._user_role_repo.assign_role(user_id, role.id, company_id)

    async def remove_role(
        self,
        user_id: uuid.UUID,
        role_name: str,
        company_id: uuid.UUID | None = None,
    ) -> None:
        role = await self._role_repo.get_by_name(role_name)
        if role is None:
            raise ValueError(f"Role '{role_name}' not found")
        await self._user_role_repo.remove_role(user_id, role.id, company_id)

    async def get_user_roles(
        self, user_id: uuid.UUID, company_id: uuid.UUID | None = None
    ) -> list[Role]:
        user_roles = await self._user_role_repo.get_user_roles(user_id, company_id)
        return [ur.role for ur in user_roles]
