from __future__ import annotations

import asyncio

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models import User
from app.repositories.user import UserRepository


async def create_superuser() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        existing = await repo.get_by_email(settings.FIRST_SUPERUSER_EMAIL)
        if existing is not None:
            print("Superuser already exists")
            return

        session.add(
            User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                full_name=settings.FIRST_SUPERUSER_FULL_NAME,
                hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
                is_active=True,
            )
        )
        await session.commit()
        print(f"Created superuser {settings.FIRST_SUPERUSER_EMAIL}")


if __name__ == "__main__":
    asyncio.run(create_superuser())
