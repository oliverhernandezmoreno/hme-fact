from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def _load_test_env() -> None:
    env_path = Path(".env.test")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        clean_value = value.strip().strip('"')
        if os.environ.get("PYTEST_DOCKER") == "1":
            os.environ.setdefault(key, clean_value)
        else:
            os.environ[key] = clean_value


_load_test_env()

from app.api.deps import get_db_session  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import (  # noqa: E402
    DTE,
    Company,
    CompanyUser,
    Customer,
    Product,
    User,
    UserRole,
)
from tests.factories.models import (  # noqa: E402
    CompanyFactory,
    CustomerFactory,
    DTEFactory,
    DTEItemFactory,
    ProductFactory,
    UserFactory,
)


@pytest.fixture(scope="session", autouse=True)
def test_settings() -> Generator[None, None, None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    settings = get_settings()
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        await _clear_database(session)
        yield session
        await _clear_database(session)


async def _clear_database(session: AsyncSession) -> None:
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.commit()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    entity = UserFactory()
    db_session.add(entity)
    await db_session.commit()
    await db_session.refresh(entity)
    return entity


@pytest.fixture
def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def company(db_session: AsyncSession, user: User) -> Company:
    entity = CompanyFactory()
    db_session.add(entity)
    await db_session.flush()
    db_session.add(CompanyUser(company_id=entity.id, user_id=user.id, role=UserRole.OWNER))
    await db_session.commit()
    await db_session.refresh(entity)
    return entity


@pytest.fixture
def tenant_headers(auth_headers: dict[str, str], company: Company) -> dict[str, str]:
    return {**auth_headers, "X-Company-ID": str(company.id)}


@pytest_asyncio.fixture
async def customer(db_session: AsyncSession, company: Company) -> Customer:
    entity = CustomerFactory(company_id=company.id)
    db_session.add(entity)
    await db_session.commit()
    await db_session.refresh(entity)
    return entity


@pytest_asyncio.fixture
async def product(db_session: AsyncSession, company: Company) -> Product:
    entity = ProductFactory(company_id=company.id)
    db_session.add(entity)
    await db_session.commit()
    await db_session.refresh(entity)
    return entity


@pytest_asyncio.fixture
async def dte(db_session: AsyncSession, company: Company, customer: Customer) -> DTE:
    entity = DTEFactory(company_id=company.id, customer_id=customer.id)
    db_session.add(entity)
    await db_session.flush()
    db_session.add(DTEItemFactory(dte_id=entity.id))
    await db_session.commit()
    await db_session.refresh(entity)
    return entity
