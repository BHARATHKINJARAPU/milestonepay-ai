import io
import uuid
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import CriterionEvaluationStatus
from app.schemas.submission import (
    CriterionEvaluationOutputSchema,
    GeminiDeliverableEvaluationSchema,
)

client = TestClient(app)


def _create_user(account_type: str = "client"):
    """Helper to create and login a user."""
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


def _setup_agreed_project():
    """Sets up a complete agreed project with a Client, Freelancer, and agreed Milestone."""
    client_token, client_user = _create_user("client")
    fl_token, fl_user = _create_user("freelancer")

    # 1. Client creates project
    p_resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Fintech Escrow Redesign",
            "description": "Build an escrow management module with verifiable milestone payouts.",
            "budget_amount": "4000.00",
            "currency": "USD",
            "deadline": "2026-12-31",
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert p_resp.status_code == 201
    project = p_resp.json()
    project_id = project["id"]

    # 2. Add Freelancer to project
    m_resp = client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": fl_user["email"], "role": "freelancer"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert m_resp.status_code in (200, 201)

    # 3. Create milestone plan
    plan_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/manual",
        json={
            "project_summary": "Two-phase escrow integration.",
            "assumptions": ["API keys provided"],
            "risks": ["Third party downtime"],
            "milestones": [
                {
                    "sequence_number": 1,
                    "title": "Phase 1: Database & Escrow Models",
                    "description": "Implement database tables and models for escrow tracking.",
                    "deliverables": ["SQL models", "Pydantic schemas"],
                    "acceptance_criteria": [
                        "Database tables created with foreign keys",
                        "Unit test suite passing with 90% coverage",
                    ],
                    "estimated_duration_days": 5,
                    "budget_percentage": 50.0,
                    "dependencies": [],
                },
                {
                    "sequence_number": 2,
                    "title": "Phase 2: Payment Gateway Integration",
                    "description": "Connect backend API to payment sandbox.",
                    "deliverables": ["Payment webhook", "Checkout controller"],
                    "acceptance_criteria": [
                        "Webhook receives authorization event",
                        "Sandbox transaction verified",
                    ],
                    "estimated_duration_days": 5,
                    "budget_percentage": 50.0,
                    "dependencies": [1],
                },
            ],
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert plan_resp.status_code == 201
    plan = plan_resp.json()
    plan_id = plan["id"]
    milestone_1 = plan["milestones"][0]

    # 4. Submit plan for approval
    sub_plan = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/submit-for-approval",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert sub_plan.status_code == 200

    # 5. Client approves
    client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/approve",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    # 6. Freelancer approves -> AGREED!
    agree_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/approve",
        headers={"Authorization": f"Bearer {fl_token}"},
    )
    assert agree_resp.status_code == 200
    assert agree_resp.json()["status"] == "agreed"

    return {
        "client_token": client_token,
        "client_user": client_user,
        "fl_token": fl_token,
        "fl_user": fl_user,
        "project_id": project_id,
        "plan_id": plan_id,
        "milestone_id": milestone_1["id"],
    }


def _mock_eval_report(crit_1_status=CriterionEvaluationStatus.MET):
    """Fixture returning a mock Gemini deliverable evaluation schema."""
    return GeminiDeliverableEvaluationSchema(
        overall_summary="The deliverable submission demonstrates successful database schema implementation with unit tests.",
        criterion_evaluations=[
            CriterionEvaluationOutputSchema(
                criterion_id=1,
                criterion_text="Database tables created with foreign keys",
                status=crit_1_status,
                explanation="SQL logs and schema documentation prove tables were created with proper foreign keys.",
                supporting_evidence_ids=["evidence_1.txt"],
                missing_information=None,
            ),
            CriterionEvaluationOutputSchema(
                criterion_id=2,
                criterion_text="Unit test suite passing with 90% coverage",
                status=CriterionEvaluationStatus.MET,
                explanation="Test run output attached shows 100% test pass rate.",
                supporting_evidence_ids=["evidence_1.txt"],
                missing_information=None,
            ),
        ],
        identified_gaps=[],
        recommendations=["Continue with Phase 2 implementation."],
        limitations=["Live database query performance not evaluated."],
        areas_for_human_verification=["Live sandbox demonstration link."],
    )


# ============================================================================
# TESTS
# ============================================================================

def test_agreed_milestone_permits_submission():
    """1. Freelancer can create a draft submission on an agreed milestone."""
    ctx = _setup_agreed_project()
    resp = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={
            "description": "Completed Phase 1 database models and tested foreign key constraints.",
            "notes": "Used SQLAlchemy 2.0 with PostgreSQL foreign keys.",
            "demonstration_url": "https://example.com/demo",
        },
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["milestone_id"] == ctx["milestone_id"]
    assert data["attempt_number"] == 1
    assert data["status"] == "draft"
    assert len(data["acceptance_criteria_snapshot"]) == 2


def test_unapproved_milestone_blocks_submission():
    """2. Submissions are rejected if the milestone plan is not agreed."""
    client_token, _ = _create_user("client")
    fl_token, fl_user = _create_user("freelancer")

    # Project with draft plan (not agreed)
    p_resp = client.post(
        "/api/v1/projects",
        json={"title": "Unapproved Proj", "description": "Desc here 123", "budget_amount": "1000.00"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    proj_id = p_resp.json()["id"]
    client.post(f"/api/v1/projects/{proj_id}/members", json={"email": fl_user["email"], "role": "freelancer"}, headers={"Authorization": f"Bearer {client_token}"})
    plan_resp = client.post(
        f"/api/v1/projects/{proj_id}/milestone-plans/manual",
        json={
            "project_summary": "Draft plan summary here for testing",
            "milestones": [
                {
                    "sequence_number": 1,
                    "title": "Milestone 1 Setup",
                    "description": "Initial database models and setup",
                    "deliverables": ["Deliverable 1"],
                    "acceptance_criteria": ["Criterion 1"],
                    "estimated_duration_days": 5,
                    "budget_percentage": 100.0,
                    "dependencies": [],
                }
            ],
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert plan_resp.status_code == 201
    m_id = plan_resp.json()["milestones"][0]["id"]

    # Attempt submission on draft plan
    resp = client.post(
        f"/api/v1/projects/{proj_id}/milestones/{m_id}/submissions",
        json={"description": "Premature submission on draft plan."},
        headers={"Authorization": f"Bearer {fl_token}"},
    )
    assert resp.status_code == 400
    assert "agreed" in resp.json()["detail"].lower()


def test_client_cannot_submit_as_freelancer():
    """3. Client is blocked from creating a deliverable submission (403)."""
    ctx = _setup_agreed_project()
    resp = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Client trying to submit work."},
        headers={"Authorization": f"Bearer {ctx['client_token']}"},
    )
    assert resp.status_code == 403
    assert "freelancer" in resp.json()["detail"].lower()


def test_unrelated_user_cannot_submit():
    """4. Non-member user is blocked from submitting work (403)."""
    ctx = _setup_agreed_project()
    outsider_token, _ = _create_user("freelancer")

    resp = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Outsider trying to submit work."},
        headers={"Authorization": f"Bearer {outsider_token}"},
    )
    assert resp.status_code == 403


def test_valid_evidence_upload():
    """5. Valid evidence files (PDF, PNG, TXT) upload cleanly to draft submission."""
    ctx = _setup_agreed_project()
    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Submission ready for evidence upload."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    # Upload a text evidence file
    files = [
        ("files", ("test_output.txt", io.BytesIO(b"All 12 unit tests passed in 0.42s."), "text/plain"))
    ]
    up_resp = client.post(
        f"/api/v1/submissions/{sub['id']}/evidence",
        files=files,
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    assert up_resp.status_code in (200, 201)
    data = up_resp.json()
    assert len(data["evidence"]) == 1
    assert data["evidence"][0]["original_filename"] == "test_output.txt"
    assert data["evidence"][0]["media_type"] == "text/plain"
    assert len(data["evidence"][0]["sha256_hash"]) == 64


def test_unsupported_file_type_rejected():
    """6. Unsupported extensions/executables (.exe, .sh) are rejected."""
    ctx = _setup_agreed_project()
    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Testing illegal file upload."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    files = [
        ("files", ("malicious.exe", io.BytesIO(b"MZ executable header"), "application/octet-stream"))
    ]
    resp = client.post(
        f"/api/v1/submissions/{sub['id']}/evidence",
        files=files,
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    assert resp.status_code == 400
    assert "unsupported" in resp.json()["detail"].lower()


def test_excess_upload_count_rejected():
    """7 & 8. Exceeding 5 evidence files is rejected."""
    ctx = _setup_agreed_project()
    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Testing upload limit of 5 files."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    # Attempt to upload 6 files in one request
    six_files = [
        ("files", (f"log_{i}.txt", io.BytesIO(f"log content {i}".encode()), "text/plain"))
        for i in range(6)
    ]
    resp = client.post(
        f"/api/v1/submissions/{sub['id']}/evidence",
        files=six_files,
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    assert resp.status_code == 400
    assert "exceed" in resp.json()["detail"].lower()


def test_files_receive_randomized_storage_keys():
    """9. Files receive random storage keys, never exposing private path."""
    ctx = _setup_agreed_project()
    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Testing storage key randomization."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    files = [("files", ("confidential_report.txt", io.BytesIO(b"Secret content"), "text/plain"))]
    resp = client.post(
        f"/api/v1/submissions/{sub['id']}/evidence",
        files=files,
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    assert resp.status_code in (200, 201)
    ev = resp.json()["evidence"][0]
    # Verify private path is not leaked in response
    assert "storage_key" not in ev or not ev.get("storage_key", "").startswith("C:")


def test_unauthorized_evidence_download_rejected():
    """10. Outsider cannot download evidence files."""
    ctx = _setup_agreed_project()
    outsider_token, _ = _create_user("freelancer")

    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Testing download permissions."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    files = [("files", ("notes.txt", io.BytesIO(b"Project notes"), "text/plain"))]
    up_resp = client.post(
        f"/api/v1/submissions/{sub['id']}/evidence",
        files=files,
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    ev_id = up_resp.json()["evidence"][0]["id"]

    # Outsider tries download
    dl_resp = client.get(
        f"/api/v1/submissions/{sub['id']}/evidence/{ev_id}",
        headers={"Authorization": f"Bearer {outsider_token}"},
    )
    assert dl_resp.status_code == 403


def test_submission_persists_when_gemini_fails():
    """11. Submission persists and remains submitted even if Gemini evaluation fails."""
    ctx = _setup_agreed_project()
    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Work submitted during simulated AI downtime."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    with patch(
        "app.services.gemini_service.gemini_service.evaluate_deliverable",
        side_effect=RuntimeError("Gemini service outage 503"),
    ):
        submit_resp = client.post(
            f"/api/v1/submissions/{sub['id']}/submit",
            headers={"Authorization": f"Bearer {ctx['fl_token']}"},
        )
        assert submit_resp.status_code == 200
        data = submit_resp.json()
        assert data["status"] == "submitted"
        assert data["ai_review_status"] == "failed"


def test_valid_gemini_output_saved():
    """12, 14 & 15. Valid AI evaluation is saved with all criteria evaluated."""
    ctx = _setup_agreed_project()
    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Work submitted with valid mock AI evaluation."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    # Upload evidence
    client.post(
        f"/api/v1/submissions/{sub['id']}/evidence",
        files=[("files", ("schema_test.txt", io.BytesIO(b"Table schemas verified."), "text/plain"))],
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )

    mock_report = _mock_eval_report()

    with patch(
        "app.services.gemini_service.gemini_service.evaluate_deliverable",
        return_value=mock_report,
    ):
        submit_resp = client.post(
            f"/api/v1/submissions/{sub['id']}/submit",
            headers={"Authorization": f"Bearer {ctx['fl_token']}"},
        )
        assert submit_resp.status_code == 200
        data = submit_resp.json()
        assert data["status"] == "submitted"
        assert data["ai_review_status"] == "completed"
        assert len(data["ai_reviews"]) == 1
        review = data["ai_reviews"][0]
        assert len(review["evaluation_results"]) == 2
        assert review["evaluation_results"][0]["status"] == "met"


def test_duplicate_active_draft_prevented():
    """16. Cannot create two active draft submissions simultaneously for the same milestone."""
    ctx = _setup_agreed_project()
    client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "First draft submission attempt."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )

    # Attempt second draft while first is still draft
    second_resp = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Conflicting second draft."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    assert second_resp.status_code == 400
    assert "active draft" in second_resp.json()["detail"].lower()


def test_client_revision_request_workflow():
    """17 & 21. Client requests revision, and freelancer creates attempt #2, preserving history."""
    ctx = _setup_agreed_project()
    sub_1 = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Initial deliverable attempt #1."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    with patch(
        "app.services.gemini_service.gemini_service.evaluate_deliverable",
        return_value=_mock_eval_report(crit_1_status=CriterionEvaluationStatus.PARTIALLY_MET),
    ):
        client.post(
            f"/api/v1/submissions/{sub_1['id']}/submit",
            headers={"Authorization": f"Bearer {ctx['fl_token']}"},
        )

    # Client requests revision
    rev_resp = client.post(
        f"/api/v1/submissions/{sub_1['id']}/request-revision",
        json={
            "decision": "revision_requested",
            "comment": "Please add migration rollback scripts and update README documentation.",
        },
        headers={"Authorization": f"Bearer {ctx['client_token']}"},
    )
    assert rev_resp.status_code == 200
    data = rev_resp.json()
    assert data["status"] == "revision_requested"
    assert len(data["client_reviews"]) == 1
    assert data["client_reviews"][0]["decision"] == "revision_requested"

    # Freelancer can now create Attempt #2!
    sub_2 = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Attempt #2: Added rollback scripts and docs."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()
    assert sub_2["attempt_number"] == 2
    assert sub_2["status"] == "draft"

    # Verify attempt history shows both attempts
    hist_resp = client.get(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    assert hist_resp.status_code == 200
    attempts = hist_resp.json()["submissions"]
    assert len(attempts) == 2
    assert attempts[0]["attempt_number"] == 2
    assert attempts[1]["attempt_number"] == 1


def test_freelancer_cannot_approve_own_submission():
    """18. Freelancer is forbidden from approving their own work."""
    ctx = _setup_agreed_project()
    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Attempting self-approval."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    with patch(
        "app.services.gemini_service.gemini_service.evaluate_deliverable",
        return_value=_mock_eval_report(),
    ):
        client.post(f"/api/v1/submissions/{sub['id']}/submit", headers={"Authorization": f"Bearer {ctx['fl_token']}"})

    # Freelancer tries to approve
    resp = client.post(
        f"/api/v1/submissions/{sub['id']}/approve",
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    assert resp.status_code == 403


def test_client_approves_submission_and_locks():
    """19 & 20. Client approves submission, locking submission and advancing milestone to approved."""
    ctx = _setup_agreed_project()
    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Final deliverable work ready for client sign-off."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    with patch(
        "app.services.gemini_service.gemini_service.evaluate_deliverable",
        return_value=_mock_eval_report(),
    ):
        client.post(f"/api/v1/submissions/{sub['id']}/submit", headers={"Authorization": f"Bearer {ctx['fl_token']}"})

    # Client approves
    app_resp = client.post(
        f"/api/v1/submissions/{sub['id']}/approve",
        json={"decision": "approved", "comment": "Excellent work. Fully meets all criteria."},
        headers={"Authorization": f"Bearer {ctx['client_token']}"},
    )
    assert app_resp.status_code == 200
    approved_sub = app_resp.json()
    assert approved_sub["status"] == "approved"

    # Cannot upload evidence to approved submission
    illegal_upload = client.post(
        f"/api/v1/submissions/{sub['id']}/evidence",
        files=[("files", ("late_file.txt", io.BytesIO(b"Too late"), "text/plain"))],
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    )
    assert illegal_upload.status_code == 400


def test_historical_ai_reviews_preserved_on_retry():
    """22. Re-evaluating deliverable increments review_version and preserves history."""
    ctx = _setup_agreed_project()
    sub = client.post(
        f"/api/v1/projects/{ctx['project_id']}/milestones/{ctx['milestone_id']}/submissions",
        json={"description": "Deliverable for retry review testing."},
        headers={"Authorization": f"Bearer {ctx['fl_token']}"},
    ).json()

    with patch(
        "app.services.gemini_service.gemini_service.evaluate_deliverable",
        return_value=_mock_eval_report(crit_1_status=CriterionEvaluationStatus.PARTIALLY_MET),
    ):
        client.post(f"/api/v1/submissions/{sub['id']}/submit", headers={"Authorization": f"Bearer {ctx['fl_token']}"})

    # Retry evaluation
    with patch(
        "app.services.gemini_service.gemini_service.evaluate_deliverable",
        return_value=_mock_eval_report(crit_1_status=CriterionEvaluationStatus.MET),
    ):
        retry_resp = client.post(
            f"/api/v1/submissions/{sub['id']}/evaluate",
            headers={"Authorization": f"Bearer {ctx['client_token']}"},
        )
        assert retry_resp.status_code == 200
        data = retry_resp.json()
        assert len(data["ai_reviews"]) == 2
        assert data["ai_reviews"][0]["review_version"] == 2
        assert data["ai_reviews"][1]["review_version"] == 1
