"""
Pytest fixtures for the Task Management API tests.

This module sets up:
- An isolated test database (fresh for each test)
- An async HTTP client for testing endpoints
- Fixtures for registered users and authenticated clients
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db


# ---------- Test database ----------
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Fresh database for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """An async HTTP client for testing endpoints."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------- User fixtures ----------
@pytest_asyncio.fixture
async def registered_user(client):
    """Create a test user and return their info."""
    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest_asyncio.fixture
async def auth_token(client, registered_user):
    """Log in and return a JWT token."""
    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_client(client, auth_token):
    """An HTTP client with the Authorization header set."""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    yield client