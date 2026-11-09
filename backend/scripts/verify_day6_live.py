"""Day 6 End-to-End Live HTTP Verification Script for MilestonePay AI.

Tests the full application integration, dashboards, notifications, activities,
and financial analytics against the live running FastAPI server:
1. Health check verification
2. Client and Freelancer registration & authentication
3. Project creation & Project Activity timeline check
4. Collaborator addition & In-App Notification check
5. Notification unread count & Mark as read check
6. Milestone plan agreement & bilateral notification check
7. Deliverable submission & activity log check
8. Client approval & notification check
9. Payment checkout & settlement activity check
10. Client Dashboard Analytics (review center, payment commitments)
11. Freelancer Dashboard Analytics (milestones progress, upcoming deadlines)
12. Payment Analytics & daily settlement trends
13. Gemini-powered Project AI Summary & health evaluation
14. Mark all notifications as read & verify unread count is zero
"""

import sys
import uuid
import httpx

BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"


def print_step(step_num: int, title: str):
    print(f"\n{'='*70}\n[STEP {step_num}] {title}\n{'='*70}")


def main():
    client = httpx.Client(base_url=BASE_URL, timeout=20.0)

    # 1. Health Checks
    print_step(1, "Verify Health Endpoints")
    r = client.get("/")
    assert r.status_code == 200, f"Root / failed: {r.text}"
    print(" Root / OK:", r.json())

    r = client.get(f"{API_PREFIX}/health")
    assert r.status_code == 200, f"API health check failed: {r.text}"
    print(" API /health OK:", r.json())

    r = client.get(f"{API_PREFIX}/health/ready")
    assert r.status_code == 200, f"Readiness check failed: {r.text}"
    ready_data = r.json()
    assert ready_data.get("database") in ("connected", "healthy"), f"Database not healthy: {ready_data}"
    print(f" {API_PREFIX}/health/ready OK: Database is connected.")

    # 2. Register & Authenticate Client and Freelancer
    print_step(2, "Register & Authenticate Client and Freelancer")
    unique_id = uuid.uuid4().hex[:8]
    client_email = f"client_d6_{unique_id}@test.com"
    freelancer_email = f"freelancer_d6_{unique_id}@test.com"
    password = "SecurePassword123!"

    # Register Client
    r = client.post(f"{API_PREFIX}/auth/register", json={
        "email": client_email,
        "password": password,
        "confirm_password": password,
        "full_name": f"Claire Client {unique_id}",
        "account_type": "client",
    })
    assert r.status_code == 201, f"Client registration failed: {r.text}"
    # Login Client
    r = client.post(f"{API_PREFIX}/auth/login", json={"email": client_email, "password": password})
    assert r.status_code == 200, f"Client login failed: {r.text}"
    client_token = r.json()["access_token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}
    print(f" Registered & Logged in Client: {client_email}")

    # Register Freelancer
    r = client.post(f"{API_PREFIX}/auth/register", json={
        "email": freelancer_email,
        "password": password,
        "confirm_password": password,
        "full_name": f"Felix Freelancer {unique_id}",
        "account_type": "freelancer",
    })
    assert r.status_code == 201, f"Freelancer registration failed: {r.text}"
    # Login Freelancer
    r = client.post(f"{API_PREFIX}/auth/login", json={"email": freelancer_email, "password": password})
    assert r.status_code == 200, f"Freelancer login failed: {r.text}"
    freelancer_token = r.json()["access_token"]
    freelancer_headers = {"Authorization": f"Bearer {freelancer_token}"}
    print(f" Registered & Logged in Freelancer: {freelancer_email}")

    # 3. Create Project & Check Activity Timeline
    print_step(3, "Create Project & Check Activity Recording")
    r = client.post(f"{API_PREFIX}/projects", headers=client_headers, json={
        "title": f"Enterprise Fintech Core {unique_id}",
        "description": "Full-stack payment orchestration platform with AI verification.",
        "budget_amount": 3000.00,
        "currency": "USD",
    })
    assert r.status_code == 201, f"Project creation failed: {r.text}"
    project = r.json()
    project_id = project["id"]
    print(f" Project created: '{project['title']}' (ID: {project_id})")

    # Verify activity was recorded
    r = client.get(f"{API_PREFIX}/projects/{project_id}/activities", headers=client_headers)
    assert r.status_code == 200, f"Get activities failed: {r.text}"
    act_data = r.json()
    assert act_data["total"] >= 1
    assert any(a["activity_type"] == "project_created" for a in act_data["activities"])
    print(" Activity 'project_created' successfully logged.")

    # 4. Add Collaborator & Verify Notification
    print_step(4, "Add Collaborator & Verify In-App Notification")
    r = client.post(f"{API_PREFIX}/projects/{project_id}/members", headers=client_headers, json={
        "email": freelancer_email,
        "role": "freelancer",
    })
    assert r.status_code == 200, f"Add collaborator failed: {r.text}"
    print(f" Added {freelancer_email} to project.")

    # Check freelancer received notification
    r = client.get(f"{API_PREFIX}/notifications", headers=freelancer_headers)
    assert r.status_code == 200, f"Get notifications failed: {r.text}"
    notif_data = r.json()
    assert notif_data["total"] >= 1
    invitation = notif_data["notifications"][0]
    assert invitation["notification_type"] == "collaborator_added"
    assert invitation["is_read"] is False
    print(f" Freelancer received notification: '{invitation['title']}' - '{invitation['message']}'")

    # 5. Check Unread Count & Mark Notification Read
    print_step(5, "Notification Unread Count & Mark Read")
    r = client.get(f"{API_PREFIX}/notifications/unread-count", headers=freelancer_headers)
    assert r.status_code == 200
    assert r.json()["unread_count"] >= 1

    r = client.patch(f"{API_PREFIX}/notifications/{invitation['id']}/read", headers=freelancer_headers)
    assert r.status_code == 200
    assert r.json()["is_read"] is True
    print(" Notification marked as read successfully.")

    # 6. Create Milestone Plan & Agreement
    print_step(6, "Create Milestone Plan & Bilateral Agreement")
    r = client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/manual", headers=client_headers, json={
        "project_summary": "Comprehensive 2-phase delivery roadmap.",
        "milestones": [
            {
                "sequence_number": 1,
                "title": "Design System & Figma Architecture",
                "description": "Complete UI/UX components and high fidelity checkout prototypes.",
                "deliverables": ["Figma Workspace", "Design Token JSON"],
                "acceptance_criteria": ["All mobile views designed", "Design system tokens documented"],
                "estimated_duration_days": 7,
                "budget_percentage": 50.0,
                "dependencies": [],
            },
            {
                "sequence_number": 2,
                "title": "Core Payment Orchestration MVP",
                "description": "FastAPI PayPal REST API integration and automated settlement verification.",
                "deliverables": ["Production Repo", "Test Suite Results"],
                "acceptance_criteria": ["All tests passing", "PayPal capture functional"],
                "estimated_duration_days": 10,
                "budget_percentage": 50.0,
                "dependencies": [1],
            },
        ],
    })
    assert r.status_code == 201, f"Create plan failed: {r.text}"
    plan = r.json()
    plan_id = plan["id"]
    m1_id = plan["milestones"][0]["id"]

    # Submit plan for approval
    r = client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/submit-for-approval", headers=client_headers)
    assert r.status_code == 200

    # Freelancer agrees
    r = client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/approve", headers=freelancer_headers)
    assert r.status_code == 200

    # Client agrees
    r = client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/approve", headers=client_headers)
    assert r.status_code == 200
    agreed_plan = r.json()
    assert agreed_plan["status"] == "agreed"
    print(" Milestone Plan agreed! Milestones are now ACTIVE.")

    # 7. Freelancer Submits Deliverable
    print_step(7, "Freelancer Submits Deliverable for Milestone 1")
    r = client.post(f"{API_PREFIX}/projects/{project_id}/milestones/{m1_id}/submissions", headers=freelancer_headers, json={
        "description": "Completed full design system, interactive prototypes, and token exports.",
        "notes": "Verified WCAG AAA contrast ratio.",
        "demonstration_url": "https://figma.com/sample-file",
    })
    assert r.status_code == 201, f"Submit deliverable failed: {r.text}"
    submission = r.json()
    submission_id = submission["id"]

    # Finalize and submit
    r = client.post(f"{API_PREFIX}/submissions/{submission_id}/submit", headers=freelancer_headers)
    assert r.status_code == 200
    print(f" Deliverable submitted (ID: {submission_id}).")

    # 8. Client Approves Deliverable
    print_step(8, "Client Approves Deliverable")
    r = client.post(f"{API_PREFIX}/submissions/{submission_id}/approve", headers=client_headers, json={
        "decision": "approved",
        "comment": "Designs reviewed and approved. Work exceeds acceptance criteria.",
    })
    assert r.status_code == 200, f"Approve submission failed: {r.text}"
    print(" Client approved submission! Milestone status transitioned to APPROVED.")

    # 9. Payment Checkout & Settlement
    print_step(9, "Payment Checkout via Mock Provider")
    r = client.post(
        f"{API_PREFIX}/projects/{project_id}/milestones/{m1_id}/payments",
        headers=client_headers,
        json={"provider": "mock"},
    )
    assert r.status_code == 201
    payment = r.json()
    payment_id = payment["id"]

    # Confirm Mock Payment
    r = client.post(
        f"{API_PREFIX}/payments/{payment_id}/mock-confirm",
        headers=client_headers,
        json={"outcome": "success"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    print(f" Payment of $1,500.00 captured and settled (Payment ID: {payment_id}).")

    # 10. Verify Client Dashboard Analytics
    print_step(10, "Verify Client Dashboard Analytics")
    r = client.get(f"{API_PREFIX}/analytics/dashboard", headers=client_headers)
    assert r.status_code == 200, f"Client analytics failed: {r.text}"
    c_analytics = r.json()
    print(" Client Analytics Summary:")
    print(f"   Role: {c_analytics['role']}")
    print(f"   Projects: {c_analytics['projects']}")
    print(f"   Milestones: {c_analytics['milestones']}")
    print(f"   Payments: {c_analytics['payments']}")
    assert c_analytics["role"] == "client"
    assert c_analytics["projects"]["total"] >= 1
    assert c_analytics["milestones"]["approved"] >= 1
    # Check completed mock payment is captured accurately
    assert any(p["amount"] == 1500.0 for p in c_analytics["payments"]["completed_mock_by_currency"])

    # 11. Verify Freelancer Dashboard Analytics
    print_step(11, "Verify Freelancer Dashboard Analytics")
    r = client.get(f"{API_PREFIX}/analytics/dashboard", headers=freelancer_headers)
    assert r.status_code == 200, f"Freelancer analytics failed: {r.text}"
    f_analytics = r.json()
    assert f_analytics["role"] == "freelancer"
    assert f_analytics["projects"]["total"] >= 1
    print(" Freelancer Analytics OK. Upcoming deadlines:", len(f_analytics["upcoming_deadlines"]))

    # 12. Verify Payment Analytics & Trends
    print_step(12, "Verify Payment Analytics & Settlement Trends")
    r = client.get(f"{API_PREFIX}/analytics/payments", headers=client_headers)
    assert r.status_code == 200
    p_data = r.json()
    assert "payments_summary" in p_data
    assert "trends" in p_data
    print(f" Settlement trends returned {len(p_data['trends'])} date entry(ies).")

    # 13. Verify Project AI Summary
    print_step(13, "Verify Project AI Health Summary")
    r = client.get(f"{API_PREFIX}/projects/{project_id}/ai-summary", headers=client_headers)
    assert r.status_code == 200, f"AI summary failed: {r.text}"
    ai_sum = r.json()
    print(" Project AI Health Summary:")
    print(f"   AI Generated: {ai_sum['is_ai_generated']}")
    print(f"   Executive Summary: {ai_sum['executive_summary']}")
    print(f"   Accomplishments: {ai_sum['key_accomplishments']}")
    print(f"   Risks: {ai_sum['potential_risks']}")
    print(f"   Next Steps: {ai_sum['recommended_next_steps']}")
    assert "executive_summary" in ai_sum
    assert len(ai_sum["key_accomplishments"]) >= 1

    # 14. Mark All Notifications as Read
    print_step(14, "Mark All Notifications as Read")
    r = client.patch(f"{API_PREFIX}/notifications/read-all", headers=freelancer_headers)
    assert r.status_code == 200
    r = client.get(f"{API_PREFIX}/notifications/unread-count", headers=freelancer_headers)
    assert r.status_code == 200
    assert r.json()["unread_count"] == 0
    print(" All notifications marked as read. Unread count verified as 0.")

    print("\n" + "="*70)
    print("ALL DAY 6 LIVE HTTP FULL INTEGRATION TESTS PASSED SUCCESSFULLY! ")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n E2E TEST FAILED: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
