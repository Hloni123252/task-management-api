"""
Tests for the authentication endpoints.
"""


# ---------- Register tests ----------
async def test_register_success(client):
    """Test successful user registration."""
    response = await client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert data["is_active"] is True
    assert "id" in data
    # Password should NEVER appear in response
    assert "password" not in data
    assert "hashed_password" not in data


async def test_register_duplicate_email(client):
    """Test that duplicate email is rejected."""
    await client.post(
        "/auth/register",
        json={
            "email": "dupe@example.com",
            "username": "user1",
            "password": "password123",
        },
    )
    response = await client.post(
        "/auth/register",
        json={
            "email": "dupe@example.com",
            "username": "user2",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


async def test_register_duplicate_username(client):
    """Test that duplicate username is rejected."""
    await client.post(
        "/auth/register",
        json={
            "email": "user1@example.com",
            "username": "sameuser",
            "password": "password123",
        },
    )
    response = await client.post(
        "/auth/register",
        json={
            "email": "user2@example.com",
            "username": "sameuser",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]


async def test_register_invalid_email(client):
    """Test that invalid email is rejected by validation."""
    response = await client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "username": "user1",
            "password": "password123",
        },
    )
    assert response.status_code == 422


async def test_register_short_password(client):
    """Test that short password is rejected."""
    response = await client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "username": "user1",
            "password": "123",
        },
    )
    assert response.status_code == 422


# ---------- Login tests ----------
async def test_login_success(client, registered_user):
    """Test successful login returns a JWT token."""
    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


async def test_login_wrong_password(client, registered_user):
    """Test login with wrong password returns 401."""
    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


async def test_login_unknown_email(client):
    """Test login with unknown email returns 401."""
    response = await client.post(
        "/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "anypassword",
        },
    )
    assert response.status_code == 401


# ---------- /auth/me tests ----------
async def test_get_me_authenticated(auth_client):
    """Test /auth/me returns current user with valid token."""
    response = await auth_client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


async def test_get_me_without_token(client):
    """Test /auth/me without token returns 401."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


async def test_get_me_invalid_token(client):
    """Test /auth/me with invalid token returns 401."""
    client.headers["Authorization"] = "Bearer invalidtoken123"
    response = await client.get("/auth/me")
    assert response.status_code == 401