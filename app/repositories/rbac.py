from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from app.models.rbac import Permission, Role, RolePermission, UserRole
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    model = Role

    async def get_by_name(self, name: str) -> Role | None:
        result = await self.session.scalars(select(Role).where(Role.name == name))
        return result.first()

    async def get_all_system(self) -> list[Role]:
        result = await self.session.scalars(select(Role).where(Role.is_system == True))
        return list(result)

    async def get_with_permissions(self, role_id: uuid.UUID) -> Role | None:
        result = await self.session.scalars(
            select(Role)
            .options(joinedload(Role.permissions).joinedload(RolePermission.permission))
            .where(Role.id == role_id)
        )
        return result.first()


class PermissionRepository(BaseRepository[Permission]):
    model = Permission

    async def get_by_module_action(
        self, module: str, action: str, resource: str
    ) -> Permission | None:
        result = await self.session.scalars(
            select(Permission).where(
                Permission.module == module,
                Permission.action == action,
                Permission.resource == resource,
            )
        )
        return result.first()

    async def get_all(self) -> list[Permission]:
        result = await self.session.scalars(select(Permission))
        return list(result)


class UserRoleRepository(BaseRepository[UserRole]):
    model = UserRole

    async def get_user_roles(
        self, user_id: uuid.UUID, company_id: uuid.UUID | None = None
    ) -> list[UserRole]:
        query = (
            select(UserRole)
            .options(
                joinedload(UserRole.role)
                .joinedload(Role.permissions)
                .joinedload(RolePermission.permission)
            )
            .where(UserRole.user_id == user_id)
        )
        if company_id is not None:
            query = query.where((UserRole.company_id == company_id) | (UserRole.company_id == None))
        result = await self.session.scalars(query)
        return list(result.unique())

    async def has_role(
        self, user_id: uuid.UUID, role_name: str, company_id: uuid.UUID | None = None
    ) -> bool:
        query = (
            select(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, Role.name == role_name)
        )
        if company_id is not None:
            query = query.where((UserRole.company_id == company_id) | (UserRole.company_id == None))
        result = await self.session.scalars(query)
        return result.first() is not None

    async def assign_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        company_id: uuid.UUID | None = None,
    ) -> UserRole:
        # Check if already assigned
        existing = await self.session.scalars(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.company_id == company_id,
            )
        )
        existing_role = existing.first()
        if existing_role:
            return existing_role
        return await self.create({"user_id": user_id, "role_id": role_id, "company_id": company_id})

    async def remove_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
        company_id: uuid.UUID | None = None,
    ) -> None:
        await self.session.execute(
            delete(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.company_id == company_id,
            )
        )
        await self.session.commit()

    async def get_user_permissions(
        self, user_id: uuid.UUID, company_id: uuid.UUID | None = None
    ) -> set[tuple[str, str, str]]:
        """Returns set of (module, action, resource) tuples for the user."""
        user_roles = await self.get_user_roles(user_id, company_id)
        permissions: set[tuple[str, str, str]] = set()
        for ur in user_roles:
            for rp in ur.role.permissions:
                perm = rp.permission
                permissions.add((perm.module, perm.action, perm.resource))
        return permissions
