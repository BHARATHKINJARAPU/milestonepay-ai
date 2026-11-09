import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.milestone import GeneratedMilestoneSchema, GeminiProjectAnalysisSchema

client = TestClient(app)


def _create_user_and_token(account_type: str = "client"):
    """Helper to register and login a test user."""
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
    return login_resp.json()["access_token"], login_resp.json()["user"]


def _create_test_project(token: str, budget: str = "3000.00", currency: str = "USD"):
    """Helper to create a project under an authenticated user."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/api/v1/projects",
        json={
            "title": "Fintech Dashboard Redesign",
            "description": "Redesign transaction workflows with real-time analytics and escrow release.",
            "budget_amount": budget,
            "currency": currency,
            "deadline": "2026-12-31",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()


def _mock_valid_gemini_analysis():
    """Returns a valid GeminiProjectAnalysisSchema fixture."""
    return GeminiProjectAnalysisSchema(
        project_summary="A comprehensive fintech dashboard with transaction monitoring and payment escrow.",
        assumptions=["User authentication is already configured", "Client will provide brand guidelines"],
        clarifying_questions=["Do you require dark mode support?"],
        risks=["Tight deadline for end-to-end integration"],
        needs_clarification=False,
        milestones=[
            GeneratedMilestoneSchema(
                sequence_number=1,
                title="UI Architecture & Wireframes",
                description="Design wireframes and set up React dashboard component layout.",
                deliverables=["Figma high-fidelity prototypes", "Design tokens"],
                acceptance_criteria=["All 5 views designed", "Client signs off on wireframes"],
                estimated_duration_days=7,
                budget_percentage=Decimal("30.0"),
                dependencies=[],
            ),
            GeneratedMilestoneSchema(
                sequence_number=2,
                title="Frontend Implementation & Integration",
                description="Implement React components and connect to backend APIs.",
                deliverables=["Dashboard screens", "API integration layer"],
                acceptance_criteria=["All API endpoints connected", "Zero console errors"],
                estimated_duration_days=14,
                budget_percentage=Decimal("40.0"),
                dependencies=[1],
            ),
            GeneratedMilestoneSchema(
                sequence_number=3,
                title="QA, Testing & Deployment",
                description="Comprehensive unit testing, bug fixing, and production deployment.",
                deliverables=["Automated test suite", "Production build"],
                acceptance_criteria=["100% critical test pass rate", "Deployed to production"],
                estimated_duration_days=7,
                budget_percentage=Decimal("30.0"),
                dependencies=[2],
            ),
        ],
    )


# ----------------------------------------------------------------------------
# 1. Successful AI Milestone Generation
# ----------------------------------------------------------------------------
def test_generate_ai_milestone_plan_success():
    """Verify successful generation of an AI milestone plan with mock Gemini service."""
    client_token, _ = _create_user_and_token("client")
    project = _create_test_project(client_token, budget="3000.00")
    project_id = project["id"]

    mock_analysis = _mock_valid_gemini_analysis()

    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        return_value=mock_analysis,
    ):
        resp = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={"additional_instructions": "Focus on high performance and clean UX."},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert resp.status_code == 201
        data = resp.json()

        assert data["project_id"] == project_id
        assert data["version"] == 1
        assert data["status"] == "draft"
        assert data["generation_source"] == "ai"
        assert len(data["milestones"]) == 3

        # Verify exact budget allocations sum to 3000.00
        milestone_amounts = [Decimal(str(m["amount"])) for m in data["milestones"]]
        assert sum(milestone_amounts) == Decimal("3000.00")
        assert data["milestones"][0]["sequence_number"] == 1
        assert data["milestones"][0]["title"] == "UI Architecture & Wireframes"
        assert len(data["milestones"][0]["deliverables"]) == 2
        assert len(data["milestones"][0]["acceptance_criteria"]) == 2


# ----------------------------------------------------------------------------
# 2. Missing Gemini API Key Error Handling
# ----------------------------------------------------------------------------
def test_generate_ai_milestone_plan_missing_api_key():
    """Verify that when GEMINI_API_KEY is not configured, a clear 400 error is returned."""
    client_token, _ = _create_user_and_token("client")
    project = _create_test_project(client_token)
    project_id = project["id"]

    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        side_effect=ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in the backend environment."),
    ):
        resp = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert resp.status_code == 400
        assert "Gemini API key is not configured" in resp.json()["detail"]


# ----------------------------------------------------------------------------
# 3. Invalid Gemini Response Rejection
# ----------------------------------------------------------------------------
def test_generate_ai_milestone_plan_invalid_response():
    """Verify that an invalid or malformed Gemini output raises an appropriate error."""
    client_token, _ = _create_user_and_token("client")
    project = _create_test_project(client_token)
    project_id = project["id"]

    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        side_effect=ValueError("Failed to parse Gemini output: Malformed JSON"),
    ):
        resp = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert resp.status_code == 400
        assert "Malformed JSON" in resp.json()["detail"]


# ----------------------------------------------------------------------------
# 4. Prompt Builder Passes Project Title and Description
# ----------------------------------------------------------------------------
def test_prompt_builder_includes_title_and_description():
    """Verify that the Gemini prompt builder receives the project's title and description."""
    client_token, _ = _create_user_and_token("client")
    project = _create_test_project(client_token)
    project_id = project["id"]

    mock_analysis = _mock_valid_gemini_analysis()

    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        return_value=mock_analysis,
    ) as mock_gen:
        resp = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={"additional_instructions": "Custom note for prompt."},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert resp.status_code == 201

        # Check the prompt argument passed to generate_milestone_plan
        assert mock_gen.called
        call_args = mock_gen.call_args[1]
        prompt = call_args["prompt"]
        assert "Fintech Dashboard Redesign" in prompt
        assert "Redesign transaction workflows" in prompt
        assert "Custom note for prompt." in prompt


# ----------------------------------------------------------------------------
# 5. Unauthenticated Request Rejection (401)
# ----------------------------------------------------------------------------
def test_unauthenticated_request_rejected():
    """Verify that unauthenticated requests to milestone endpoints return 401."""
    random_uuid = uuid.uuid4()
    resp = client.get(f"/api/v1/projects/{random_uuid}/milestone-plans")
    assert resp.status_code == 401


# ----------------------------------------------------------------------------
# 6. Non-Member Access Rejection (403)
# ----------------------------------------------------------------------------
def test_non_member_access_forbidden():
    """Verify that an authenticated user who is not a project member cannot view or modify plans."""
    client_token, _ = _create_user_and_token("client")
    outsider_token, _ = _create_user_and_token("freelancer")

    project = _create_test_project(client_token)
    project_id = project["id"]

    resp = client.get(
        f"/api/v1/projects/{project_id}/milestone-plans",
        headers={"Authorization": f"Bearer {outsider_token}"},
    )
    assert resp.status_code == 403
    assert "access" in resp.json()["detail"].lower()


# ----------------------------------------------------------------------------
# 7. Exact Cent Financial Calculation & Rounding Discrepancy
# ----------------------------------------------------------------------------
def test_milestone_financial_exact_cent_sum():
    """Verify that milestone amounts sum to the exact cent of project total budget, even with repeating fractions."""
    client_token, _ = _create_user_and_token("client")
    # Budget of $1000.00 split 3 ways (33.333...%)
    project = _create_test_project(client_token, budget="1000.00")
    project_id = project["id"]

    uneven_analysis = GeminiProjectAnalysisSchema(
        project_summary="Three equal phase split.",
        assumptions=[],
        clarifying_questions=[],
        risks=[],
        needs_clarification=False,
        milestones=[
            GeneratedMilestoneSchema(
                sequence_number=1,
                title="Phase 1",
                description="Description 1",
                deliverables=["D1"],
                acceptance_criteria=["AC1"],
                estimated_duration_days=5,
                budget_percentage=Decimal("33.3333"),
                dependencies=[],
            ),
            GeneratedMilestoneSchema(
                sequence_number=2,
                title="Phase 2",
                description="Description 2",
                deliverables=["D2"],
                acceptance_criteria=["AC2"],
                estimated_duration_days=5,
                budget_percentage=Decimal("33.3333"),
                dependencies=[1],
            ),
            GeneratedMilestoneSchema(
                sequence_number=3,
                title="Phase 3",
                description="Description 3",
                deliverables=["D3"],
                acceptance_criteria=["AC3"],
                estimated_duration_days=5,
                budget_percentage=Decimal("33.3334"),
                dependencies=[2],
            ),
        ],
    )

    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        return_value=uneven_analysis,
    ):
        resp = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        amounts = [Decimal(str(m["amount"])) for m in data["milestones"]]
        assert sum(amounts) == Decimal("1000.00")


# ----------------------------------------------------------------------------
# 8. Circular Dependency Detection
# ----------------------------------------------------------------------------
def test_circular_dependency_rejection():
    """Verify that circular milestone dependencies are caught and rejected."""
    client_token, _ = _create_user_and_token("client")
    project = _create_test_project(client_token)
    project_id = project["id"]

    manual_payload = {
        "project_summary": "Circular plan",
        "milestones": [
            {
                "sequence_number": 1,
                "title": "Task 1",
                "description": "Desc 1",
                "deliverables": ["D1"],
                "acceptance_criteria": ["A1"],
                "estimated_duration_days": 3,
                "budget_percentage": 50.0,
                "dependencies": [2],  # Circular: 1 depends on 2 and 2 depends on 1
            },
            {
                "sequence_number": 2,
                "title": "Task 2",
                "description": "Desc 2",
                "deliverables": ["D2"],
                "acceptance_criteria": ["A2"],
                "estimated_duration_days": 3,
                "budget_percentage": 50.0,
                "dependencies": [1],
            },
        ],
    }

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/manual",
        json=manual_payload,
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert resp.status_code == 400
    assert "dependency" in resp.json()["detail"].lower()


# ----------------------------------------------------------------------------
# 9. Create Manual Milestone Plan
# ----------------------------------------------------------------------------
def test_create_manual_milestone_plan():
    """Verify that a member can manually author a structured milestone plan."""
    client_token, _ = _create_user_and_token("client")
    project = _create_test_project(client_token, budget="2000.00")
    project_id = project["id"]

    manual_payload = {
        "project_summary": "Manually structured delivery plan.",
        "assumptions": ["Client provides API keys"],
        "risks": ["Third party rate limits"],
        "milestones": [
            {
                "sequence_number": 1,
                "title": "Sprint 1: Core Setup",
                "description": "Initialize database and auth",
                "deliverables": ["Auth modules", "Database models"],
                "acceptance_criteria": ["All tests pass"],
                "estimated_duration_days": 5,
                "budget_percentage": 50.0,
                "dependencies": [],
            },
            {
                "sequence_number": 2,
                "title": "Sprint 2: Payments",
                "description": "Integrate payments",
                "deliverables": ["Payment webhook", "Checkout flow"],
                "acceptance_criteria": ["Sandbox transactions verified"],
                "estimated_duration_days": 5,
                "budget_percentage": 50.0,
                "dependencies": [1],
            },
        ],
    }

    resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/manual",
        json=manual_payload,
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["generation_source"] == "manual"
    assert data["status"] == "draft"
    assert len(data["milestones"]) == 2
    assert Decimal(str(data["milestones"][0]["amount"])) == Decimal("1000.00")
    assert Decimal(str(data["milestones"][1]["amount"])) == Decimal("1000.00")


# ----------------------------------------------------------------------------
# 10. Update Draft Plan
# ----------------------------------------------------------------------------
def test_update_draft_plan():
    """Verify that draft plans can be modified."""
    client_token, _ = _create_user_and_token("client")
    project = _create_test_project(client_token)
    project_id = project["id"]

    mock_analysis = _mock_valid_gemini_analysis()
    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        return_value=mock_analysis,
    ):
        gen_resp = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        plan_id = gen_resp.json()["id"]

    # Update summary and assumptions
    patch_resp = client.patch(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}",
        json={
            "project_summary": "Updated summary with clarified timeline.",
            "assumptions": ["Updated assumption A", "Updated assumption B"],
        },
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["project_summary"] == "Updated summary with clarified timeline."
    assert len(updated["assumptions"]) == 2


# ----------------------------------------------------------------------------
# 11 & 12. Submit Plan For Approval Flow (Role Requirement)
# ----------------------------------------------------------------------------
def test_submit_for_approval_requires_both_roles():
    """Submitting for approval must fail if project lacks either Client or Freelancer member."""
    client_token, _ = _create_user_and_token("client")
    project = _create_test_project(client_token)
    project_id = project["id"]

    mock_analysis = _mock_valid_gemini_analysis()
    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        return_value=mock_analysis,
    ):
        gen_resp = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        plan_id = gen_resp.json()["id"]

    # Attempt to submit with only Client member
    sub_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/submit-for-approval",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert sub_resp.status_code == 400
    assert "freelancer" in sub_resp.json()["detail"].lower()


# ----------------------------------------------------------------------------
# 13 & 14. Bilateral Agreement Workflow & Immutability
# ----------------------------------------------------------------------------
def test_bilateral_approval_and_plan_agreement():
    """Verify two-party agreement: Client and Freelancer both approve, marking plan 'agreed'."""
    client_token, client_user = _create_user_and_token("client")
    freelancer_token, freelancer_user = _create_user_and_token("freelancer")

    # 1. Client creates project
    project = _create_test_project(client_token)
    project_id = project["id"]

    # 2. Add Freelancer as member
    add_member_resp = client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": freelancer_user["email"], "role": "freelancer"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert add_member_resp.status_code in (200, 201)

    # 3. Generate AI plan
    mock_analysis = _mock_valid_gemini_analysis()
    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        return_value=mock_analysis,
    ):
        gen_resp = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        plan_id = gen_resp.json()["id"]

    # 4. Submit plan for approval
    submit_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/submit-for-approval",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert submit_resp.status_code == 200
    assert submit_resp.json()["status"] == "pending_approval"

    # 5. Plan cannot be edited while pending approval
    patch_attempt = client.patch(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}",
        json={"project_summary": "Illegal edit during review"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert patch_attempt.status_code == 400

    # 6. Client approves
    client_approve_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/approve",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert client_approve_resp.status_code == 200
    # Still pending_approval because freelancer hasn't approved yet
    assert client_approve_resp.json()["status"] == "pending_approval"
    assert len(client_approve_resp.json()["reviews"]) == 1

    # 7. Duplicate client approval is idempotent
    dup_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/approve",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert dup_resp.status_code == 200
    assert len(dup_resp.json()["reviews"]) == 1

    # 8. Freelancer approves -> Plan transitions to AGREED!
    fl_approve_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/approve",
        headers={"Authorization": f"Bearer {freelancer_token}"},
    )
    assert fl_approve_resp.status_code == 200
    final_plan = fl_approve_resp.json()
    assert final_plan["status"] == "agreed"
    assert len(final_plan["reviews"]) == 2

    # 9. Verify parent project advanced from draft to active
    proj_resp = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert proj_resp.status_code == 200
    assert proj_resp.json()["status"] == "active"

    # 10. Agreed plan cannot be edited
    agreed_patch_attempt = client.patch(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}",
        json={"project_summary": "Another illegal edit"},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert agreed_patch_attempt.status_code == 400


# ----------------------------------------------------------------------------
# 15. Revision Request Workflow
# ----------------------------------------------------------------------------
def test_revision_request_workflow():
    """Verify that requesting changes sets status to revision_requested and permits edits."""
    client_token, client_user = _create_user_and_token("client")
    freelancer_token, freelancer_user = _create_user_and_token("freelancer")

    project = _create_test_project(client_token)
    project_id = project["id"]

    client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"email": freelancer_user["email"], "role": "freelancer"},
        headers={"Authorization": f"Bearer {client_token}"},
    )

    mock_analysis = _mock_valid_gemini_analysis()
    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        return_value=mock_analysis,
    ):
        gen_resp = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        plan_id = gen_resp.json()["id"]

    # Submit for approval
    client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/submit-for-approval",
        headers={"Authorization": f"Bearer {client_token}"},
    )

    # Freelancer requests revision
    rev_resp = client.post(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}/request-revision",
        json={"comment": "Please extend Sprint 2 duration by 5 days for QA."},
        headers={"Authorization": f"Bearer {freelancer_token}"},
    )
    assert rev_resp.status_code == 200
    assert rev_resp.json()["status"] == "revision_requested"

    # Client can now edit the plan in revision_requested status
    edit_resp = client.patch(
        f"/api/v1/projects/{project_id}/milestone-plans/{plan_id}",
        json={"project_summary": "Updated after freelancer revision request."},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert edit_resp.status_code == 200
    assert edit_resp.json()["project_summary"] == "Updated after freelancer revision request."


# ----------------------------------------------------------------------------
# 16. List and Retrieve Milestone Plans
# ----------------------------------------------------------------------------
def test_list_and_get_milestone_plans():
    """Verify listing all versions for a project and retrieving single plan details."""
    client_token, _ = _create_user_and_token("client")
    project = _create_test_project(client_token)
    project_id = project["id"]

    mock_analysis = _mock_valid_gemini_analysis()
    with patch(
        "app.services.gemini_service.gemini_service.generate_milestone_plan",
        return_value=mock_analysis,
    ):
        # Version 1
        client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        # Version 2
        gen_v2 = client.post(
            f"/api/v1/projects/{project_id}/milestone-plans/generate",
            json={"additional_instructions": "Second proposal variation"},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        v2_id = gen_v2.json()["id"]

    # List plans
    list_resp = client.get(
        f"/api/v1/projects/{project_id}/milestone-plans",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] == 2
    assert len(data["plans"]) == 2
    assert data["plans"][0]["version"] == 2
    assert data["plans"][1]["version"] == 1

    # Get single plan
    get_resp = client.get(
        f"/api/v1/projects/{project_id}/milestone-plans/{v2_id}",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == v2_id
    assert get_resp.json()["version"] == 2
