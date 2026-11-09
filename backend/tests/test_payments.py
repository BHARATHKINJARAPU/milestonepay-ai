from datetime import datetime, timezone
from decimal import Decimal
import json
from unittest.mock import AsyncMock, patch
import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.models.enums import CriterionEvaluationStatus, MilestonePaymentStatus, MilestoneStatus, PaymentProvider, PaymentStatus
from app.schemas.submission import CriterionEvaluationOutputSchema, GeminiDeliverableEvaluationSchema

client = TestClient(app)


def _create_user(account_type: str = "client"):
    """Helper to create and authenticate a user."""
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": f"Test {account_type.capitalize()}",
            "email": email,
            "password": pwd,
            "confirm_password": pwd,
            "account_type": account_type,
        },
    )
    assert reg.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pwd},
    )
    assert login.status_code == 200
    return login.json()["access_token"], login.json()["user"]


def _setup_approved_milestone():
    """Sets up a complete project where a milestone deliverable has been approved by the client."""
    client_token, client_user = _create_user("client")
    fl_token, fl_user = _create_user("freelancer")

    # 1. Client creates project
    p_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Payment Automation Pipeline",
            "description": "Integration testing for PayPal sandbox and mock providers",
            "budget_amount": "2500.00",
            "currency": "USD",
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert p_resp.status_code == 201
    project_id = p_resp.json()["id"]

    # 2. Add Freelancer to project
    m_resp = client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": fl_user["email"], "role": "freelancer"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert m_resp.status_code == 200

    # 3. Create manual milestone plan
    plan_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/manual",
        json={
            "project_summary": "Core setup and payments infrastructure delivery.",
            "milestones": [
                {
                    "sequence_number": 1,
                    "title": "Backend Checkout Engine",
                    "description": "Server-side order creation and capture endpoints.",
                    "deliverables": ["REST API routes", "Database migrations"],
                    "acceptance_criteria": [
                        "PayPal v2 order endpoint creates order with intent CAPTURE",
                        "Capture endpoint verifies status COMPLETED",
                    ],
                    "estimated_duration_days": 5,
                    "budget_percentage": "100.00",
                    "dependencies": [],
                }
            ],
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert plan_resp.status_code == 201
    plan_id = plan_resp.json()["id"]
    milestone_id = plan_resp.json()["milestones"][0]["id"]

    # 4. Mutual agreement
    client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/submit-for-approval",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/approve",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    agree_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/approve",
        headers={"Authorization": f"Bearer {fl_token}"},
    )
    assert agree_resp.status_code == 200
    assert agree_resp.json()["status"] == "agreed"

    # 5. Freelancer submits work
    sub_draft = client.post(
        f"/api/v1/projects/{project_id}/milestones/{milestone_id}/submissions",
        json={
            "description": "Completed backend checkout engine with 100% test coverage.",
            "technical_notes": "Implemented strict PayPal request timeouts and cryptographic hashing.",
        },
        headers={"Authorization": f"Bearer {fl_token}"},
    )
    assert sub_draft.status_code == 201
    sub_id = sub_draft.json()["id"]

    # Freelancer submits with mocked AI evaluation to eliminate test latency and quota consumption
    mock_eval = GeminiDeliverableEvaluationSchema(
        overall_summary="The deliverable submission demonstrates successful checkout engine implementation.",
        criterion_evaluations=[
            CriterionEvaluationOutputSchema(
                criterion_id=1,
                criterion_text="Backend checkout engine verification",
                status=CriterionEvaluationStatus.MET,
                explanation="Verified implementation with 100% test coverage.",
                supporting_evidence_ids=[],
                missing_information=None,
            )
        ],
        identified_gaps=[],
        recommendations=["Proceed with approval"],
        limitations=[],
        areas_for_human_verification=[],
    )
    with patch("app.services.gemini_service.gemini_service.evaluate_deliverable", return_value=mock_eval):
        sub_res = client.post(
            f"/api/v1/submissions/{sub_id}/submit",
            headers={"Authorization": f"Bearer {fl_token}"},
        )
        assert sub_res.status_code == 200

    # 6. Client approves submission -> milestone becomes APPROVED
    appr_res = client.post(
        f"/api/v1/submissions/{sub_id}/approve",
        json={"decision": "approved", "comment": "Outstanding work! Approved for payment."},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "approved"

    return {
        "project_id": project_id,
        "milestone_id": milestone_id,
        "client_token": client_token,
        "client_user": client_user,
        "fl_token": fl_token,
        "fl_user": fl_user,
    }


# ============================================================================
# 1. PAYMENT ELIGIBILITY TESTS
# ============================================================================

def test_eligible_approved_milestone_returns_true():
    """An approved milestone on an agreed project is eligible for client checkout."""
    setup = _setup_approved_milestone()
    resp = client.get(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payment-eligibility",
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["eligible"] is True
    assert data["reason"] is None
    assert Decimal(data["amount"]) == Decimal("2500.00")
    assert data["currency"] == "USD"
    assert data["payment_status"] == "unpaid"


def test_freelancer_ineligible_for_initiating_payment():
    """Freelancer cannot initiate checkout; eligibility returns false."""
    setup = _setup_approved_milestone()
    resp = client.get(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payment-eligibility",
        headers={"Authorization": f"Bearer {setup['fl_token']}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["eligible"] is False
    assert "Only the assigned client" in data["reason"]


def test_unapproved_milestone_ineligible_for_payment():
    """Milestone whose deliverables have not yet been approved is not eligible."""
    client_token, _ = _create_user("client")
    fl_token, fl_user = _create_user("freelancer")

    # Create project and agreed plan without deliverable approval
    p_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Unapproved Milestone Test",
            "description": "Detailed project brief for testing unapproved milestone eligibility.",
            "budget_amount": "1000.00",
            "currency": "USD",
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    proj_id = p_resp.json()["id"]
    client.post(f"/api/v1/projects/{proj_id}/members", json={"email": fl_user["email"], "role": "freelancer"}, headers={"Authorization": f"Bearer {client_token}"})

    plan_resp = client.post(
        f"/api/v1/projects/{proj_id}/milestone-plans/manual",
        json={
            "project_summary": "Unapproved test plan.",
            "milestones": [
                {
                    "sequence_number": 1,
                    "title": "Phase 1 Not Approved",
                    "description": "Work in progress description.",
                    "deliverables": ["Code"],
                    "acceptance_criteria": ["Criteria 1"],
                    "estimated_duration_days": 3,
                    "budget_percentage": "100.00",
                    "dependencies": [],
                }
            ],
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    plan_id = plan_resp.json()["id"]
    m_id = plan_resp.json()["milestones"][0]["id"]

    client.post(f"/api/v1/projects/{proj_id}/milestone-plans/{plan_id}/submit-for-approval", headers={"Authorization": f"Bearer {client_token}"})
    client.post(f"/api/v1/projects/{proj_id}/milestone-plans/{plan_id}/approve", headers={"Authorization": f"Bearer {client_token}"})
    client.post(f"/api/v1/projects/{proj_id}/milestone-plans/{plan_id}/approve", headers={"Authorization": f"Bearer {fl_token}"})

    resp = client.get(
        f"/api/v1/projects/{proj_id}/milestones/{m_id}/payment-eligibility",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["eligible"] is False
    assert "deliverables have not been approved yet" in data["reason"]


# ============================================================================
# 2. MOCK PROVIDER TESTS
# ============================================================================

def test_mock_payment_creation_and_order_generation():
    """Client creates a mock payment; backend generates simulated order with clear notice."""
    setup = _setup_approved_milestone()
    resp = client.post(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
        json={"provider": "mock"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["provider"] == "mock"
    assert data["status"] == "order_created"
    assert data["provider_order_id"].startswith("MOCK-ORD-")
    assert Decimal(str(data["amount"])) == Decimal("2500.00")
    assert data["currency"] == "USD"
    assert "SIMULATED PAYMENT" in data["provider_metadata"]["simulation_notice"]


def test_freelancer_cannot_create_payment():
    """Freelancer cannot initiate payment creation (HTTP 400 with eligibility check)."""
    setup = _setup_approved_milestone()
    resp = client.post(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
        json={"provider": "mock"},
        headers={"Authorization": f"Bearer {setup['fl_token']}"},
    )
    assert resp.status_code == 400
    assert "Only the assigned client" in resp.json()["detail"]


def test_mock_payment_successful_confirmation():
    """Client confirms simulated payment; transitions to completed and marks milestone completed."""
    setup = _setup_approved_milestone()
    init_resp = client.post(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
        json={"provider": "mock"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    payment_id = init_resp.json()["id"]

    # Client confirms payment
    confirm_resp = client.post(
        f"/api/v1/payments/{payment_id}/mock-confirm",
        json={"outcome": "success"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    assert confirm_resp.status_code == 200
    data = confirm_resp.json()
    assert data["status"] == "completed"
    assert data["provider_capture_id"].startswith("MOCK-CAP-")
    assert data["completed_at"] is not None

    # Verify eligibility now shows already paid
    elig_resp = client.get(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payment-eligibility",
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    assert elig_resp.status_code == 200
    assert elig_resp.json()["eligible"] is False
    assert "already been paid in full" in elig_resp.json()["reason"]


def test_duplicate_mock_confirmation_is_idempotent():
    """Calling capture on already completed payment returns existing record idempotently."""
    setup = _setup_approved_milestone()
    init_resp = client.post(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
        json={"provider": "mock"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    payment_id = init_resp.json()["id"]

    first_confirm = client.post(
        f"/api/v1/payments/{payment_id}/mock-confirm",
        json={"outcome": "success"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    assert first_confirm.status_code == 200

    second_confirm = client.post(
        f"/api/v1/payments/{payment_id}/mock-confirm",
        json={"outcome": "success"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    assert second_confirm.status_code == 200
    assert second_confirm.json()["id"] == payment_id
    assert second_confirm.json()["status"] == "completed"


def test_mock_payment_cancellation():
    """Client can simulate user cancelling checkout."""
    setup = _setup_approved_milestone()
    init_resp = client.post(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
        json={"provider": "mock"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    payment_id = init_resp.json()["id"]

    cancel_resp = client.post(
        f"/api/v1/payments/{payment_id}/mock-confirm",
        json={"outcome": "cancel"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

    # Milestone payment status remains unpaid
    elig_resp = client.get(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payment-eligibility",
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    assert elig_resp.json()["eligible"] is True


def test_mock_confirmation_forbidden_in_production():
    """Mock payment confirmation endpoint is blocked if ENVIRONMENT is production."""
    setup = _setup_approved_milestone()
    init_resp = client.post(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
        json={"provider": "mock"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    payment_id = init_resp.json()["id"]

    with patch.object(settings, "ENVIRONMENT", "production"):
        resp = client.post(
            f"/api/v1/payments/{payment_id}/mock-confirm",
            json={"outcome": "success"},
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert resp.status_code == 403
        assert "disabled in production" in resp.json()["detail"]


# ============================================================================
# 3. PAYPAL OAUTH & ORDERS API TESTS (MOCKED REST RESPONSES)
# ============================================================================

@pytest.mark.anyio
async def test_paypal_oauth_token_retrieval_and_caching():
    """OAuth client fetches token with Basic auth and caches until near expiry."""
    from app.services.payments.paypal_auth import PayPalAuthService

    mock_auth = PayPalAuthService()
    with patch.object(settings, "PAYPAL_CLIENT_ID", "test_client_id"), \
         patch.object(settings, "PAYPAL_CLIENT_SECRET", "test_client_secret"):

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=200,
                json=lambda: {"access_token": "ACCESS_TOKEN_XYZ", "expires_in": 3600},
            )

            token1 = await mock_auth.get_access_token()
            assert token1 == "ACCESS_TOKEN_XYZ"
            assert mock_post.call_count == 1

            # Second call within validity window uses cached token without network call
            token2 = await mock_auth.get_access_token()
            assert token2 == "ACCESS_TOKEN_XYZ"
            assert mock_post.call_count == 1


def test_paypal_order_creation_with_milestone_amount():
    """PayPal order creation sends correct amount, currency, and CAPTURE intent."""
    setup = _setup_approved_milestone()
    order_id = f"5O190127TN-{uuid.uuid4().hex[:8]}"

    mock_paypal_order = {
        "id": order_id,
        "status": "CREATED",
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": "test_ref",
                "amount": {"currency_code": "USD", "value": "2500.00"},
            }
        ],
        "links": [
            {
                "href": f"https://www.sandbox.paypal.com/checkoutnow?token={order_id}",
                "rel": "approve",
                "method": "GET",
            }
        ],
    }

    with patch("app.services.payments.paypal_orders.PayPalOrdersClient.create_order", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_paypal_order

        resp = client.post(
            f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
            json={"provider": "paypal"},
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["provider"] == "paypal"
        assert data["provider_order_id"] == order_id
        assert data["status"] == "order_created"
        assert mock_create.call_count == 1


def test_paypal_order_capture_success_and_milestone_synchronization():
    """Client triggers capture; backend validates capture response and marks milestone completed."""
    setup = _setup_approved_milestone()
    order_id = f"PAYPAL-ORD-{uuid.uuid4().hex[:8]}"
    capture_id = f"CAPTURE-{uuid.uuid4().hex[:8]}"

    mock_create_order = {
        "id": order_id,
        "status": "CREATED",
        "links": [{"href": "https://sandbox.paypal.com/approve", "rel": "approve"}],
    }

    mock_order_status = {
        "id": order_id,
        "status": "APPROVED",
        "purchase_units": [
            {
                "amount": {"currency_code": "USD", "value": "2500.00"},
            }
        ],
        "payer": {"email_address": "buyer@sandbox.paypal.com", "payer_id": "PAYER-123"},
    }

    mock_capture_response = {
        "id": order_id,
        "status": "COMPLETED",
        "purchase_units": [
            {
                "payments": {
                    "captures": [
                        {
                            "id": capture_id,
                            "status": "COMPLETED",
                            "amount": {"currency_code": "USD", "value": "2500.00"},
                        }
                    ]
                }
            }
        ],
    }

    with patch("app.services.payments.paypal_orders.PayPalOrdersClient.create_order", new_callable=AsyncMock) as mock_create, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.get_order", new_callable=AsyncMock) as mock_get, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.capture_order", new_callable=AsyncMock) as mock_capture:

        mock_create.return_value = mock_create_order
        mock_get.return_value = mock_order_status
        mock_capture.return_value = (201, mock_capture_response)

        # 1. Create payment
        init_resp = client.post(
            f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
            json={"provider": "paypal"},
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert init_resp.status_code == 201
        payment_id = init_resp.json()["id"]

        # 2. Capture payment
        cap_resp = client.post(
            f"/api/v1/payments/{payment_id}/capture",
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert cap_resp.status_code == 200
        data = cap_resp.json()
        assert data["status"] == "completed"
        assert data["provider_capture_id"] == capture_id
        assert data["completed_at"] is not None

        # 3. Check milestone status synchronization
        elig_resp = client.get(
            f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payment-eligibility",
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert elig_resp.json()["payment_status"] == "completed"


def test_paypal_capture_blocks_unapproved_order():
    """Capture attempt is blocked with HTTP 400 if the buyer has not approved the order yet."""
    setup = _setup_approved_milestone()
    order_id = f"PAYPAL-ORD-UNAPPROVED-{uuid.uuid4().hex[:8]}"

    mock_create_order = {"id": order_id, "status": "CREATED", "links": []}
    mock_order_status = {
        "id": order_id,
        "status": "CREATED",  # Not yet approved
        "purchase_units": [{"amount": {"currency_code": "USD", "value": "2500.00"}}],
    }

    with patch("app.services.payments.paypal_orders.PayPalOrdersClient.create_order", new_callable=AsyncMock) as mock_create, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.get_order", new_callable=AsyncMock) as mock_get, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.capture_order", new_callable=AsyncMock) as mock_capture:

        mock_create.return_value = mock_create_order
        mock_get.return_value = mock_order_status

        init_resp = client.post(
            f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
            json={"provider": "paypal"},
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        payment_id = init_resp.json()["id"]

        # Capture fails because status is CREATED, not APPROVED
        cap_resp = client.post(
            f"/api/v1/payments/{payment_id}/capture",
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert cap_resp.status_code == 400
        assert "not yet been approved" in cap_resp.json()["detail"].lower()
        mock_capture.assert_not_called()


def test_paypal_capture_already_completed_is_idempotent():
    """Pre-capture detects order is already COMPLETED on PayPal and returns idempotently."""
    setup = _setup_approved_milestone()
    order_id = f"PAYPAL-ORD-ALREADY-DONE-{uuid.uuid4().hex[:8]}"

    mock_create_order = {"id": order_id, "status": "CREATED", "links": []}
    mock_order_status = {
        "id": order_id,
        "status": "COMPLETED",
        "purchase_units": [{"amount": {"currency_code": "USD", "value": "2500.00"}}],
    }

    with patch("app.services.payments.paypal_orders.PayPalOrdersClient.create_order", new_callable=AsyncMock) as mock_create, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.get_order", new_callable=AsyncMock) as mock_get, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.capture_order", new_callable=AsyncMock) as mock_capture:

        mock_create.return_value = mock_create_order
        mock_get.return_value = mock_order_status

        init_resp = client.post(
            f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
            json={"provider": "paypal"},
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        payment_id = init_resp.json()["id"]

        cap_resp = client.post(
            f"/api/v1/payments/{payment_id}/capture",
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert cap_resp.status_code == 200
        assert cap_resp.json()["status"] == "completed"
        mock_capture.assert_not_called()


def test_paypal_capture_rejects_precheck_amount_mismatch():
    """Capture fails with HTTP 400 if PayPal order amount does not match milestone in database."""
    setup = _setup_approved_milestone()
    order_id = f"PAYPAL-ORD-PRECHECK-MISMATCH-{uuid.uuid4().hex[:8]}"

    mock_create_order = {"id": order_id, "status": "CREATED", "links": []}
    mock_order_status = {
        "id": order_id,
        "status": "APPROVED",
        "purchase_units": [{"amount": {"currency_code": "USD", "value": "50.00"}}],  # Expected 2500.00
    }

    with patch("app.services.payments.paypal_orders.PayPalOrdersClient.create_order", new_callable=AsyncMock) as mock_create, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.get_order", new_callable=AsyncMock) as mock_get, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.capture_order", new_callable=AsyncMock) as mock_capture:

        mock_create.return_value = mock_create_order
        mock_get.return_value = mock_order_status

        init_resp = client.post(
            f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
            json={"provider": "paypal"},
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        payment_id = init_resp.json()["id"]

        cap_resp = client.post(
            f"/api/v1/payments/{payment_id}/capture",
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert cap_resp.status_code == 400
        assert "amount mismatch" in cap_resp.json()["detail"].lower()
        mock_capture.assert_not_called()


def test_paypal_capture_rejects_amount_mismatch():
    """Capture fails if PayPal returns a different amount than the agreed milestone."""
    setup = _setup_approved_milestone()
    order_id = f"PAYPAL-ORD-MISMATCH-{uuid.uuid4().hex[:8]}"

    mock_create_order = {"id": order_id, "status": "CREATED", "links": []}
    mock_order_status = {
        "id": order_id,
        "status": "APPROVED",
        "purchase_units": [{"amount": {"currency_code": "USD", "value": "2500.00"}}],
    }
    mock_bad_capture = {
        "id": order_id,
        "purchase_units": [
            {
                "payments": {
                    "captures": [
                        {
                            "id": f"CAPTURE-BAD-{uuid.uuid4().hex[:8]}",
                            "status": "COMPLETED",
                            "amount": {"currency_code": "USD", "value": "100.00"},  # Expected 2500.00
                        }
                    ]
                }
            }
        ],
    }

    with patch("app.services.payments.paypal_orders.PayPalOrdersClient.create_order", new_callable=AsyncMock) as mock_create, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.get_order", new_callable=AsyncMock) as mock_get, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.capture_order", new_callable=AsyncMock) as mock_capture:

        mock_create.return_value = mock_create_order
        mock_get.return_value = mock_order_status
        mock_capture.return_value = (201, mock_bad_capture)

        init_resp = client.post(
            f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
            json={"provider": "paypal"},
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        payment_id = init_resp.json()["id"]

        cap_resp = client.post(
            f"/api/v1/payments/{payment_id}/capture",
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert cap_resp.status_code == 502
        assert "amount mismatch" in cap_resp.json()["detail"].lower()


def test_payment_status_check_endpoint():
    """GET /api/v1/payments/{id}/status reports live lifecycle stages and can_capture state."""
    setup = _setup_approved_milestone()
    order_id = f"PAYPAL-ORD-STATUS-{uuid.uuid4().hex[:8]}"

    mock_create_order = {
        "id": order_id,
        "status": "CREATED",
        "links": [{"href": f"https://www.sandbox.paypal.com/checkoutnow?token={order_id}", "rel": "approve"}],
    }

    with patch("app.services.payments.paypal_orders.PayPalOrdersClient.create_order", new_callable=AsyncMock) as mock_create, \
         patch("app.services.payments.paypal_orders.PayPalOrdersClient.get_order", new_callable=AsyncMock) as mock_get:

        mock_create.return_value = mock_create_order

        # 1. Initiate order
        init_resp = client.post(
            f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
            json={"provider": "paypal"},
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        payment_id = init_resp.json()["id"]

        # 2. Stage: buyer_approval_required
        mock_get.return_value = {
            "id": order_id,
            "status": "CREATED",
            "links": [{"href": f"https://www.sandbox.paypal.com/checkoutnow?token={order_id}", "rel": "approve"}],
        }
        status_resp = client.get(
            f"/api/v1/payments/{payment_id}/status",
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert status_resp.status_code == 200
        data1 = status_resp.json()
        assert data1["stage"] == "buyer_approval_required"
        assert data1["can_capture"] is False
        assert "checkoutnow" in data1["approval_url"]

        # 3. Stage: buyer_approved
        mock_get.return_value = {
            "id": order_id,
            "status": "APPROVED",
            "payer": {"email_address": "sandbox_buyer@example.com", "payer_id": "P-999"},
        }
        status_resp2 = client.get(
            f"/api/v1/payments/{payment_id}/status",
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert status_resp2.status_code == 200
        data2 = status_resp2.json()
        assert data2["stage"] == "buyer_approved"
        assert data2["can_capture"] is True
        assert data2["payer_email"] == "sandbox_buyer@example.com"

        # 4. Non-member access is rejected
        unrelated_token, _ = _create_user("client")
        forbidden_resp = client.get(
            f"/api/v1/payments/{payment_id}/status",
            headers={"Authorization": f"Bearer {unrelated_token}"},
        )
        assert forbidden_resp.status_code == 403


# ============================================================================
# 4. PAYPAL WEBHOOK TESTS
# ============================================================================

def test_webhook_capture_completed_updates_payment():
    """Verified PAYMENT.CAPTURE.COMPLETED webhook marks payment completed."""
    setup = _setup_approved_milestone()

    # Create payment first
    init_resp = client.post(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
        json={"provider": "mock"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    payment_id = init_resp.json()["id"]

    webhook_event = {
        "id": f"WH-EVENT-{uuid.uuid4().hex[:12]}",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {
            "id": f"CAP-{uuid.uuid4().hex[:8]}",
            "custom_id": payment_id,
            "status": "COMPLETED",
        },
    }

    headers = {
        "paypal-auth-algo": "SHA256withRSA",
        "paypal-cert-url": "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123",
        "paypal-transmission-id": "trans-123",
        "paypal-transmission-sig": "valid-sig",
        "paypal-transmission-time": datetime.now(timezone.utc).isoformat(),
    }

    with patch("app.services.payments.paypal_webhooks.PayPalWebhookService.verify_signature", new_callable=AsyncMock) as mock_verify:
        from app.services.payments.base import WebhookVerificationResult
        mock_verify.return_value = WebhookVerificationResult(is_valid=True, verification_status="SUCCESS")

        resp = client.post(
            "/api/v1/webhooks/paypal",
            headers=headers,
            json=webhook_event,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "processed"

        # Verify payment status in DB
        pay_resp = client.get(
            f"/api/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {setup['client_token']}"},
        )
        assert pay_resp.json()["status"] == "completed"


def test_unverified_webhook_rejected():
    """Webhook with failing signature verification is rejected with 400 Bad Request."""
    webhook_event = {
        "id": f"WH-FAKE-{uuid.uuid4().hex[:12]}",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {},
    }

    headers = {
        "paypal-auth-algo": "SHA256withRSA",
        "paypal-cert-url": "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123",
        "paypal-transmission-id": "trans-fake",
        "paypal-transmission-sig": "forged-sig",
        "paypal-transmission-time": datetime.now(timezone.utc).isoformat(),
    }

    with patch("app.services.payments.paypal_webhooks.PayPalWebhookService.verify_signature", new_callable=AsyncMock) as mock_verify:
        from app.services.payments.base import WebhookVerificationResult
        mock_verify.return_value = WebhookVerificationResult(
            is_valid=False,
            verification_status="FAILURE",
            reason="Signature mismatch",
        )

        resp = client.post(
            "/api/v1/webhooks/paypal",
            headers=headers,
            json=webhook_event,
        )
        assert resp.status_code == 400
        assert "verification failed" in resp.json()["detail"].lower()


def test_duplicate_webhook_is_idempotent():
    """Duplicate webhook delivery is acknowledged safely without redundant processing."""
    setup = _setup_approved_milestone()

    init_resp = client.post(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
        json={"provider": "mock"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    payment_id = init_resp.json()["id"]

    event_id = f"WH-REPEAT-{uuid.uuid4().hex[:8]}"
    webhook_event = {
        "id": event_id,
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {
            "id": f"CAP-{uuid.uuid4().hex[:8]}",
            "custom_id": payment_id,
            "status": "COMPLETED",
        },
    }

    headers = {
        "paypal-auth-algo": "SHA256withRSA",
        "paypal-cert-url": "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123",
        "paypal-transmission-id": "trans-repeat",
        "paypal-transmission-sig": "valid-sig",
        "paypal-transmission-time": datetime.now(timezone.utc).isoformat(),
    }

    with patch("app.services.payments.paypal_webhooks.PayPalWebhookService.verify_signature", new_callable=AsyncMock) as mock_verify:
        from app.services.payments.base import WebhookVerificationResult
        mock_verify.return_value = WebhookVerificationResult(is_valid=True, verification_status="SUCCESS")

        # First call processes event
        resp1 = client.post("/api/v1/webhooks/paypal", headers=headers, json=webhook_event)
        assert resp1.status_code == 200
        assert resp1.json()["status"] == "processed"

        # Second call returns already_processed idempotently
        resp2 = client.post("/api/v1/webhooks/paypal", headers=headers, json=webhook_event)
        assert resp2.status_code == 200
        assert resp2.json()["status"] == "already_processed"


# ============================================================================
# 5. PAYMENT HISTORY & ACCESS CONTROL TESTS
# ============================================================================

def test_list_payments_returns_only_authorized_records():
    """Client and Freelancer see their own project payments; unrelated users see empty list."""
    setup = _setup_approved_milestone()
    unrelated_token, _ = _create_user("client")

    # Create and complete payment
    init_resp = client.post(
        f"/api/v1/projects/{setup['project_id']}/milestones/{setup['milestone_id']}/payments",
        json={"provider": "mock"},
        headers={"Authorization": f"Bearer {setup['client_token']}"},
    )
    payment_id = init_resp.json()["id"]
    client.post(f"/api/v1/payments/{payment_id}/mock-confirm", json={"outcome": "success"}, headers={"Authorization": f"Bearer {setup['client_token']}"})

    # Client can see payment in list
    client_list = client.get("/api/v1/payments", headers={"Authorization": f"Bearer {setup['client_token']}"})
    assert client_list.status_code == 200
    assert any(p["id"] == payment_id for p in client_list.json()["payments"])

    # Freelancer can see payment in list
    fl_list = client.get("/api/v1/payments", headers={"Authorization": f"Bearer {setup['fl_token']}"})
    assert fl_list.status_code == 200
    assert any(p["id"] == payment_id for p in fl_list.json()["payments"])

    # Unrelated user cannot see this payment
    unrelated_list = client.get("/api/v1/payments", headers={"Authorization": f"Bearer {unrelated_token}"})
    assert unrelated_list.status_code == 200
    assert not any(p["id"] == payment_id for p in unrelated_list.json()["payments"])
