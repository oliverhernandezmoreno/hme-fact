from __future__ import annotations

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import create_access_token, verify_password
from app.models import User
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)

    async def authenticate(self, *, email: str, password: str) -> User:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AppError("Invalid credentials", status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            raise AppError("Inactive user", status.HTTP_403_FORBIDDEN)
        return user

    def create_access_token(self, user: User) -> str:
        return create_access_token(str(user.id))
