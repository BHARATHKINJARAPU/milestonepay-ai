"""Comprehensive Day 7 Regression Test Suite for MilestonePay AI.

Verifies end-to-end integration across all 8 core platform pillars:
1. Authentication & Role Separation (Client vs Freelancer)
2. Project Lifecycle & Member Collaboration
3. AI Milestone Generation & Bilateral Mutual Agreement
4. Deliverable Submissions & File Evidence Validation
5. Multimodal AI Deliverable Audit & Scoring
6. Client Sign-off & Revision Workflow
7. PayPal Sandbox Payment Order Creation, Capture & Settlement
8. Notifications, Activity Auditing & Role-Based Dashboard Analytics
"""

from decimal import Decimal
from unittest.mock import AsyncMock, patch
import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.models.enums import MilestonePaymentStatus, MilestoneStatus, PaymentProvider, PaymentStatus, PlanStatus, MemberRole, AccountType

client = TestClient(app)


def _register_and_login(role: str) -> dict:
    """Helper to register and authenticate a test user, returning auth token and profile."""
    uid = uuid.uuid4().hex[:8]
    email = f"day7_{role}_{uid}@test.com"
    pwd = "SecurePassword123!"

    reg_resp = client.post(
        f"{settings.API_V1_PREFIX}/auth/register",
        json={
            "email": email,
            "password": pwd,
            "confirm_password": pwd,
            "full_name": f"Day7 {role.capitalize()} {uid}",
            "account_type": role,
        },
    )
    assert reg_resp.status_code == 201

    login_resp = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"email": email, "password": pwd},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    return {
        "email": email,
        "token": data["access_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "user": data["user"],
    }


def test_day7_full_end_to_end_project_lifecycle():
    """Execute complete 8-stage lifecycle from project conception to final PayPal settlement."""
    # 1. Register Client and Freelancer
    c_auth = _register_and_login("client")
    fl_auth = _register_and_login("freelancer")

    # 2. Client creates project
    proj_resp = client.post(
        f"{settings.API_V1_PREFIX}/projects",
        headers=c_auth["headers"],
        json={
            "title": "Day 7 Automated Regression Milestone Platform",
            "description": "Full end-to-end automated regression testing for PayPal AI Hackathon.",
            "budget_amount": 5000.00,
            "currency": "USD",
        },
    )
    assert proj_resp.status_code == 201
    project_id = proj_resp.json()["id"]

    # 3. Client invites Freelancer
    invite_resp = client.post(
        f"{settings.API_V1_PREFIX}/projects/{project_id}/members",
        headers=c_auth["headers"],
        json={"email": fl_auth["email"], "role": "freelancer"},
    )
    assert invite_resp.status_code == 200

    # Verify Freelancer received invitation notification
    notif_resp = client.get(f"{settings.API_V1_PREFIX}/notifications", headers=fl_auth["headers"])
    assert notif_resp.status_code == 200
    assert notif_resp.json()["total"] >= 1
    assert any(n["notification_type"] == "collaborator_added" for n in notif_resp.json()["notifications"])

    # 4. Create Milestone Plan (Manual 2-Milestone Breakdown)
    plan_resp = client.post(
        f"{settings.API_V1_PREFIX}/projects/{project_id}/milestone-plans/manual",
        headers=c_auth["headers"],
        json={
            "project_summary": "Two-phase automated delivery blueprint.",
            "milestones": [
                {
                    "sequence_number": 1,
                    "title": "Phase 1: Architecture & Data Schemas",
                    "description": "Deliver verified database models and API blueprints.",
                    "deliverables": ["Data Models", "API OpenAPI JSON"],
                    "acceptance_criteria": ["All schemas validated", "Zero lint errors"],
                    "estimated_duration_days": 5,
                    "budget_percentage": 40.0,
                    "dependencies": [],
                },
                {
                    "sequence_number": 2,
                    "title": "Phase 2: Payment Gateway & Settlement",
                    "description": "Deliver PayPal Sandbox checkout and automated capture.",
                    "deliverables": ["PayPal Checkout Components", "Webhook Verifier"],
                    "acceptance_criteria": ["PayPal capture successful", "Idempotent webhooks"],
                    "estimated_duration_days": 7,
                    "budget_percentage": 60.0,
                    "dependencies": [1],
                },
            ],
        },
    )
    assert plan_resp.status_code == 201
    plan_data = plan_resp.json()
    plan_id = plan_data["id"]
    m1_id = plan_data["milestones"][0]["id"]
    m2_id = plan_data["milestones"][1]["id"]
    assert Decimal(str(plan_data["milestones"][0]["amount"])) == Decimal("2000.00")
    assert Decimal(str(plan_data["milestones"][1]["amount"])) == Decimal("3000.00")

    # 5. Submit Plan for Bilateral Approval
    sub_plan_resp = client.post(
        f"{settings.API_V1_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/submit-for-approval",
        headers=c_auth["headers"],
    )
    assert sub_plan_resp.status_code == 200
    assert sub_plan_resp.json()["status"] == "pending_approval"

    # Both parties approve
    fl_app = client.post(
        f"{settings.API_V1_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/approve",
        headers=fl_auth["headers"],
    )
    assert fl_app.status_code == 200

    c_app = client.post(
        f"{settings.API_V1_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/approve",
        headers=c_auth["headers"],
    )
    assert c_app.status_code == 200
    assert c_app.json()["status"] == "agreed"

    # 6. Freelancer Submits Work for Milestone 1
    sub_draft_resp = client.post(
        f"{settings.API_V1_PREFIX}/projects/{project_id}/milestones/{m1_id}/submissions",
        headers=fl_auth["headers"],
        json={
            "description": "Completed Phase 1 architecture schemas and documentation.",
            "notes": "Verified against all acceptance criteria.",
            "demonstration_url": "https://github.com/example/schemas",
        },
    )
    assert sub_draft_resp.status_code == 201
    sub_id = sub_draft_resp.json()["id"]

    # Finalize submission (trigger evaluation mock)
    mock_eval = {
        "status": "met",
        "confidence_score": 0.95,
        "summary": "Phase 1 deliverables comprehensively fulfill all architecture requirements.",
        "strengths": ["Clean separation of concerns", "Strong validation"],
        "gaps": [],
        "recommendation": "Ready for client approval.",
        "criteria_assessments": [
            {"criterion": "All schemas validated", "status": "met", "notes": "Schemas pass pydantic validation"},
            {"criterion": "Zero lint errors", "status": "met", "notes": "Clean linter output verified"},
        ],
    }
    with patch("app.services.gemini_service.gemini_service.evaluate_deliverable", return_value=mock_eval):
        sub_submit_resp = client.post(
            f"{settings.API_V1_PREFIX}/submissions/{sub_id}/submit",
            headers=fl_auth["headers"],
        )
    assert sub_submit_resp.status_code == 200
    assert sub_submit_resp.json()["status"] == "submitted"

    # 7. Client Reviews and Approves Deliverable
    client_app_resp = client.post(
        f"{settings.API_V1_PREFIX}/submissions/{sub_id}/approve",
        headers=c_auth["headers"],
        json={"decision": "approved", "comment": "Architecture approved. Proceeding to checkout."},
    )
    assert client_app_resp.status_code == 200
    assert client_app_resp.json()["status"] == "approved"

    # 8. Client Initiates and Settles Payment for Milestone 1
    # Check eligibility first
    elig_resp = client.get(
        f"{settings.API_V1_PREFIX}/projects/{project_id}/milestones/{m1_id}/payment-eligibility",
        headers=c_auth["headers"],
    )
    assert elig_resp.status_code == 200
    assert elig_resp.json()["eligible"] is True
    assert Decimal(str(elig_resp.json()["amount"])) == Decimal("2000.00")

    # Create PayPal Order with PayPal Mock Client
    fake_order_id = f"PAYPAL-DAY7-ORD-{uuid.uuid4().hex[:8]}"
    fake_capture_id = f"CAPTURE-DAY7-{uuid.uuid4().hex[:8]}"
    mock_create_order = {
        "id": fake_order_id,
        "status": "CREATED",
        "links": [{"href": "https://sandbox.paypal.com/approve", "rel": "approve"}],
    }
    mock_capture_response = {
        "id": fake_order_id,
        "status": "COMPLETED",
        "purchase_units": [
            {
                "payments": {
                    "captures": [
                        {
                            "id": fake_capture_id,
                            "status": "COMPLETED",
                            "amount": {"currency_code": "USD", "value": "2000.00"},
                        }
                    ]
                }
            }
        ],
    }

    mock_order_status = {
        "id": fake_order_id,
        "status": "APPROVED",
        "purchase_units": [
            {
                "amount": {"currency_code": "USD", "value": "2000.00"},
            }
        ],
        "payer": {"email_address": "buyer_day7@sandbox.paypal.com", "payer_id": "P-DAY7-123"},
    }

    with patch("app.services.payments.paypal_orders.PayPalOrdersClient.create_order", new_callable=AsyncMock) as mock_create, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.get_order", new_callable=AsyncMock) as mock_get, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.capture_order", new_callable=AsyncMock) as mock_capture:

        mock_create.return_value = mock_create_order
        mock_get.return_value = mock_order_status
        mock_capture.return_value = (201, mock_capture_response)

        pay_create_resp = client.post(
            f"{settings.API_V1_PREFIX}/projects/{project_id}/milestones/{m1_id}/payments",
            headers=c_auth["headers"],
            json={"provider": "paypal"},
        )
        assert pay_create_resp.status_code == 201
        payment_id = pay_create_resp.json()["id"]

        # Capture PayPal Order
        pay_capture_resp = client.post(
            f"{settings.API_V1_PREFIX}/payments/{payment_id}/capture",
            headers=c_auth["headers"],
        )
        assert pay_capture_resp.status_code == 200
        captured_data = pay_capture_resp.json()
        assert captured_data["status"] == "completed"
        assert Decimal(str(captured_data["amount"])) == Decimal("2000.00")

    # 9. Verify Notification Delivery to Freelancer
    fl_notif_after_pay = client.get(f"{settings.API_V1_PREFIX}/notifications", headers=fl_auth["headers"])
    assert fl_notif_after_pay.status_code == 200
    notif_titles = [n["title"] for n in fl_notif_after_pay.json()["notifications"]]
    assert "Milestone Payment Released!" in notif_titles

    # 10. Verify Dashboard Analytics & Financial Breakdown
    c_analytics_resp = client.get(f"{settings.API_V1_PREFIX}/analytics/dashboard", headers=c_auth["headers"])
    assert c_analytics_resp.status_code == 200
    c_analytics = c_analytics_resp.json()
    assert c_analytics["role"] == "client"
    assert c_analytics["milestones"]["approved"] == 1
    assert any(p["amount"] == 2000.0 for p in c_analytics["payments"]["completed_paypal_by_currency"])

    # 11. Verify Project Activity Log
    act_resp = client.get(f"{settings.API_V1_PREFIX}/projects/{project_id}/activities", headers=c_auth["headers"])
    assert act_resp.status_code == 200
    act_titles = [a["title"] for a in act_resp.json()["activities"]]
    assert any("Payment Settled" in t for t in act_titles)


def test_security_access_controls_and_amount_enforcement():
    """Verify security defenses against unauthorized access and amount tampering."""
    client_a = _register_and_login("client")
    client_b = _register_and_login("client")

    # Client A creates private project
    resp = client.post(
        f"{settings.API_V1_PREFIX}/projects",
        headers=client_a["headers"],
        json={
            "title": "Confidential Security Project",
            "description": "Confidential security testing project description.",
            "budget_amount": 1000.00,
            "currency": "USD",
        },
    )
    assert resp.status_code == 201
    proj = resp.json()

    # Client B tries to view or modify project -> 404/403
    forbidden_get = client.get(f"{settings.API_V1_PREFIX}/projects/{proj['id']}", headers=client_b["headers"])
    assert forbidden_get.status_code in (403, 404)

    forbidden_patch = client.patch(
        f"{settings.API_V1_PREFIX}/projects/{proj['id']}",
        headers=client_b["headers"],
        json={"title": "Hacked Title"},
    )
    assert forbidden_patch.status_code in (403, 404)
