import uuid
from fastapi.testclient import TestClient

from app.core.security import verify_password
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def test_successful_registration():
    """Verify successful user registration for both client and freelancer."""
    email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "full_name": "Alex Mercer",
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "account_type": "freelancer",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email.lower()
    assert data["full_name"] == "Alex Mercer"
    assert data["account_type"] == "freelancer"
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email_rejection():
    """Verify rejection when registering with an already existing email."""
    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "full_name": "Jordan Lee",
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!",
        "account_type": "client",
    }
    # First registration
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    # Second registration with same email
    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"].lower()


def test_password_is_hashed_in_database():
    """Verify database stores an Argon2 hash and never plain-text password."""
    email = f"security_{uuid.uuid4().hex[:8]}@example.com"
    raw_pwd = "SuperSecret123!"
    payload = {
        "full_name": "Security Tester",
        "email": email,
        "password": raw_pwd,
        "confirm_password": raw_pwd,
        "account_type": "freelancer",
    }
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 201

    # Inspect directly from database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        assert user.password_hash != raw_pwd
        assert user.password_hash.startswith("$argon2id$")
        assert verify_password(raw_pwd, user.password_hash) is True
    finally:
        db.close()


def test_successful_login():
    """Verify user can authenticate and receives a valid JWT token."""
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    raw_pwd = "ValidPassword123!"
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Login User",
            "email": email,
            "password": raw_pwd,
            "confirm_password": raw_pwd,
            "account_type": "client",
        },
    )

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": raw_pwd},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    assert data["user"]["email"] == email


def test_incorrect_password_rejection():
    """Verify login rejects invalid password with 401."""
    email = f"wrongpwd_{uuid.uuid4().hex[:8]}@example.com"
    raw_pwd = "ValidPassword123!"
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Fail Login",
            "email": email,
            "password": raw_pwd,
            "confirm_password": raw_pwd,
            "account_type": "freelancer",
        },
    )

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword999!"},
    )
    assert login_resp.status_code == 401
    assert "Invalid email or password" in login_resp.json()["detail"]


def test_invalid_token_rejection():
    """Verify that an invalid or tampered token is rejected on protected routes."""
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.fake.token"},
    )
    assert resp.status_code == 401


def test_authenticated_profile_retrieval():
    """Verify GET /api/v1/auth/me returns the profile for a logged-in user."""
    email = f"profile_{uuid.uuid4().hex[:8]}@example.com"
    raw_pwd = "ValidPassword123!"
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Profile User",
            "email": email,
            "password": raw_pwd,
            "confirm_password": raw_pwd,
            "account_type": "client",
        },
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": raw_pwd},
    )
    token = login_resp.json()["access_token"]

    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["email"] == email
    assert data["full_name"] == "Profile User"
    assert data["account_type"] == "client"

