import uuid
from decimal import Decimal
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _create_authenticated_user(account_type: str = "client"):
    """Helper to create and log in a user, returning (token, user_dict)."""
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": f"Test {account_type.capitalize()}",
            "email": email,
            "password": pwd,
            "confirm_password": pwd,
            "account_type": account_type,
        },
    )
    assert reg_resp.status_code == 201

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pwd},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return token, login_resp.json()["user"]


def test_authenticated_project_creation():
    """Verify authenticated user can create a project and is made the first member."""
    token, user = _create_authenticated_user(account_type="client")
    headers = {"Authorization": f"Bearer {token}"}

    project_payload = {
        "title": "E-Commerce Checkout Redesign",
        "description": "Full overhaul of the client checkout workflow with PayPal support.",
        "budget_amount": "3500.00",
        "currency": "USD",
        "deadline": "2026-12-31",
    }
    response = client.post("/api/v1/projects", json=project_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == project_payload["title"]
    assert Decimal(str(data["budget_amount"])) == Decimal("3500.00")
    assert data["status"] == "draft"
    assert data["created_by_id"] == user["id"]
    # Verify creator is automatic first member
    assert len(data["members"]) == 1
    assert data["members"][0]["user_id"] == user["id"]
    assert data["members"][0]["role"] == "client"


def test_project_appears_in_creator_project_list():
    """Verify that newly created project is returned in GET /api/v1/projects."""
    token, user = _create_authenticated_user(account_type="freelancer")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/projects",
        json={
            "title": "Mobile App Wireframing",
            "description": "Create high-fidelity wireframes in Figma for iOS application.",
            "budget_amount": "1200.00",
            "currency": "USD",
        },
        headers=headers,
    )

    list_resp = client.get("/api/v1/projects", headers=headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] >= 1
    assert any(p["title"] == "Mobile App Wireframing" for p in data["projects"])


def test_project_detail_retrieval():
    """Verify project details can be fetched by ID by a member."""
    token, user = _create_authenticated_user(account_type="client")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "API Backend Microservice",
            "description": "High performance FastAPI service with PostgreSQL database.",
            "budget_amount": "2000.00",
            "currency": "USD",
        },
        headers=headers,
    )
    project_id = create_resp.json()["id"]

    detail_resp = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == project_id


def test_project_update_by_creator():
    """Verify that only the creator can update project title and budget."""
    token, user = _create_authenticated_user(account_type="client")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Old Project Title",
            "description": "Initial specification description for testing update.",
            "budget_amount": "1000.00",
            "currency": "USD",
        },
        headers=headers,
    )
    project_id = create_resp.json()["id"]

    update_resp = client.patch(
        f"/api/v1/projects/{project_id}",
        json={
            "title": "Updated Modern Title",
            "budget_amount": "1750.00",
        },
        headers=headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["title"] == "Updated Modern Title"
    assert Decimal(str(data["budget_amount"])) == Decimal("1750.00")


def test_project_inaccessible_to_non_members():
    """Verify that a project cannot be read or updated by a non-member user."""
    token_owner, _ = _create_authenticated_user(account_type="client")
    token_stranger, _ = _create_authenticated_user(account_type="freelancer")

    # Creator creates project
    create_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Confidential Security Audit",
            "description": "Auditing application dependencies and secret configuration.",
            "budget_amount": "5000.00",
            "currency": "USD",
        },
        headers={"Authorization": f"Bearer {token_owner}"},
    )
    project_id = create_resp.json()["id"]

    # Stranger tries to read project
    forbidden_resp = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token_stranger}"},
    )
    assert forbidden_resp.status_code == 403
    assert "do not have access" in forbidden_resp.json()["detail"].lower()


def test_adding_complementary_registered_collaborator():
    """Verify project creator (client) can add a registered freelancer by email."""
    client_token, client_user = _create_authenticated_user(account_type="client")
    freelancer_token, freelancer_user = _create_authenticated_user(account_type="freelancer")

    # Client creates project
    create_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Dashboard Analytics Integration",
            "description": "Integrate chart visualizations and metrics cards into frontend.",
            "budget_amount": "2500.00",
            "currency": "USD",
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    project_id = create_resp.json()["id"]

    # Client adds freelancer
    add_resp = client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": freelancer_user["email"]},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert add_resp.status_code == 200
    data = add_resp.json()
    assert len(data["members"]) == 2
    roles = {m["role"] for m in data["members"]}
    assert roles == {"client", "freelancer"}

    # Verified: Freelancer can now access project details!
    fl_read = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {freelancer_token}"},
    )
    assert fl_read.status_code == 200


def test_rejecting_same_role_collaborator():
    """Verify rejection when trying to add a collaborator with the same role as creator."""
    client_token1, _ = _create_authenticated_user(account_type="client")
    _, client_user2 = _create_authenticated_user(account_type="client")

    create_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Multi-Client Test Project",
            "description": "Attempting to add a second client instead of a freelancer.",
            "budget_amount": "1500.00",
            "currency": "USD",
        },
        headers={"Authorization": f"Bearer {client_token1}"},
    )
    project_id = create_resp.json()["id"]

    add_resp = client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": client_user2["email"]},
        headers={"Authorization": f"Bearer {client_token1}"},
    )
    assert add_resp.status_code == 400
    assert "complementary" in add_resp.json()["detail"].lower()


def test_rejecting_duplicate_membership():
    """Verify rejection when trying to add an already registered member."""
    client_token, _ = _create_authenticated_user(account_type="client")
    _, freelancer_user = _create_authenticated_user(account_type="freelancer")

    create_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Duplicate Membership Check",
            "description": "Testing that adding the same user twice is cleanly rejected.",
            "budget_amount": "1000.00",
            "currency": "USD",
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    project_id = create_resp.json()["id"]

    # Add once
    r1 = client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": freelancer_user["email"]},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r1.status_code == 200

    # Add duplicate
    r2 = client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": freelancer_user["email"]},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r2.status_code == 400
    assert "already a member" in r2.json()["detail"].lower()


def test_preventing_unauthorized_updates():
    """Verify collaborator (non-creator) cannot edit project details."""
    client_token, _ = _create_authenticated_user(account_type="client")
    freelancer_token, freelancer_user = _create_authenticated_user(account_type="freelancer")

    create_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Immutable by Collaborator",
            "description": "Collaborators should not be allowed to change project metadata.",
            "budget_amount": "3000.00",
            "currency": "USD",
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    project_id = create_resp.json()["id"]

    # Add collaborator
    client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": freelancer_user["email"]},
        headers={"Authorization": f"Bearer {client_token}"},
    )

    # Freelancer tries to update
    fl_update = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {freelancer_token}"},
    )
    assert fl_update.status_code == 403
    assert "Only the project creator" in fl_update.json()["detail"]


def test_project_status_validation():
    """Verify allowed status transitions (draft -> active -> completed -> archived) and rejection of invalid ones."""
    client_token, _ = _create_authenticated_user(account_type="client")
    headers = {"Authorization": f"Bearer {client_token}"}

    create_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Status Workflow Testing",
            "description": "Testing status transition business logic and validations.",
            "budget_amount": "4000.00",
            "currency": "USD",
        },
        headers=headers,
    )
    project_id = create_resp.json()["id"]

    # 1. Invalid: draft directly to completed
    bad_transition = client.patch(
        f"/api/v1/projects/{project_id}/status",
        json={"status": "completed"},
        headers=headers,
    )
    assert bad_transition.status_code == 400
    assert "Invalid status transition" in bad_transition.json()["detail"]

    # 2. Valid: draft to active
    to_active = client.patch(
        f"/api/v1/projects/{project_id}/status",
        json={"status": "active"},
        headers=headers,
    )
    assert to_active.status_code == 200
    assert to_active.json()["status"] == "active"

    # 3. Valid: active to completed
    to_completed = client.patch(
        f"/api/v1/projects/{project_id}/status",
        json={"status": "completed"},
        headers=headers,
    )
    assert to_completed.status_code == 200
    assert to_completed.json()["status"] == "completed"

    # 4. Valid: completed to archived
    to_archived = client.patch(
        f"/api/v1/projects/{project_id}/status",
        json={"status": "archived"},
        headers=headers,
    )
    assert to_archived.status_code == 200
    assert to_archived.json()["status"] == "archived"

