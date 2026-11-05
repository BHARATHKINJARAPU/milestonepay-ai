from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db.session import get_db
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify that root endpoint provides basic service metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "MilestonePay AI"
    assert "/docs" in data["docs"]


def test_health_endpoint():
    """Verify GET /api/v1/health returns ok status and service identifier."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "ok",
        "service": "milestonepay-api",
    }


def test_health_ready_success_mocked():
    """Verify GET /api/v1/health/ready returns ready status when DB execution succeeds."""
    # Mock database session returning 1
    mock_db = MagicMock()
    mock_db.execute.return_value.scalar.return_value = 1

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "status": "ready",
            "service": "milestonepay-api",
            "database": "connected",
        }
    finally:
        app.dependency_overrides.clear()


def test_health_ready_database_down():
    """Verify GET /api/v1/health/ready returns 503 and safe error message when DB fails."""
    mock_db = MagicMock()
    mock_db.execute.side_effect = OperationalError("connection refused", params=None, orig=None)

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert "Database service is unavailable" in data["detail"]
        # Ensure sensitive database credentials or internal parameters are never exposed
        assert "password" not in data["detail"].lower()
        assert "localhost" not in data["detail"]
    finally:
        app.dependency_overrides.clear()


def test_health_ready_live_database():
    """Verify live GET /api/v1/health/ready against running PostgreSQL database."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "ready",
        "service": "milestonepay-api",
        "database": "connected",
    }


def test_cors_preflight():
    """Verify CORS preflight handling for the frontend Vite origin."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
