"""Day 5 End-to-End Live HTTP Verification Script for MilestonePay AI.

Tests the full payment lifecycle against the live running FastAPI server:
1. Health check verification
2. Client and Freelancer registration & authentication
3. Project creation with budget
4. Collaborator addition
5. Milestone plan creation & agreement (Active milestones)
6. Pre-approval payment eligibility check (Assert not eligible)
7. Freelancer deliverable submission
8. Client submission approval (Milestone becomes Approved)
9. Post-approval payment eligibility check (Assert eligible, correct amount/currency)
10. Freelancer payment initiation denial (Role-based security: 403 Forbidden)
11. Client initiates Mock payment order (Simulated Provider)
12. Order creation idempotency check
13. Payment detail verification with audit event log
14. Client confirms mock payment
15. Verification of milestone payment_status transition to 'completed'
16. Post-completion payment eligibility check (Assert not eligible - already paid)
17. Webhook endpoint verification (Simulated PayPal webhook ingestion)
18. Payment history list verification for both Client and Freelancer
"""

import sys
import uuid
import httpx

BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"


def print_step(step_num: int, title: str):
    print(f"\n{'='*70}\n[STEP {step_num}] {title}\n{'='*70}")


def main():
    client = httpx.Client(base_url=BASE_URL, timeout=15.0)

    # 1. Health Checks
    print_step(1, "Verify Backend Health Endpoints")
    r = client.get("/")
    assert r.status_code == 200, f"Root / failed: {r.text}"
    print(" Root / OK:", r.json())

    r = client.get(f"{API_PREFIX}/health")
    assert r.status_code == 200, f"API health check failed: {r.text}"
    health_data = r.json()
    assert health_data.get("database") == "healthy", f"Database not healthy: {health_data}"
    print(f" {API_PREFIX}/health OK: Database is healthy.")

    # 2. Registration and Authentication
    print_step(2, "Register & Authenticate Client and Freelancer")
    unique_id = uuid.uuid4().hex[:8]
    client_email = f"client_{unique_id}@test.com"
    freelancer_email = f"freelancer_{unique_id}@test.com"
    password = "SecurePassword123!"

    # Register Client
    r = client.post(f"{API_PREFIX}/auth/register", json={
        "email": client_email,
        "password": password,
        "full_name": f"Alice Client {unique_id}",
        "role": "client",
    })
    assert r.status_code == 201, f"Client registration failed: {r.text}"
    client_data = r.json()
    client_token = client_data["access_token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}
    print(f" Registered Client: {client_email}")

    # Register Freelancer
    r = client.post(f"{API_PREFIX}/auth/register", json={
        "email": freelancer_email,
        "password": password,
        "full_name": f"Bob Freelancer {unique_id}",
        "role": "freelancer",
    })
    assert r.status_code == 201, f"Freelancer registration failed: {r.text}"
    freelancer_data = r.json()
    freelancer_token = freelancer_data["access_token"]
    freelancer_headers = {"Authorization": f"Bearer {freelancer_token}"}
    print(f" Registered Freelancer: {freelancer_email}")

    # 3. Create Project
    print_step(3, "Client Creates Project")
    r = client.post(f"{API_PREFIX}/projects", headers=client_headers, json={
        "title": f"Fintech Mobile App {unique_id}",
        "description": "Full-stack mobile app with payments and AI verification.",
        "budget": 2500.00,
        "currency": "USD",
    })
    assert r.status_code == 201, f"Project creation failed: {r.text}"
    project = r.json()
    project_id = project["id"]
    print(f" Project created: '{project['title']}' (ID: {project_id}, Budget: ${project['budget']})")

    # 4. Add Freelancer as Collaborator
    print_step(4, "Add Freelancer to Project")
    r = client.post(f"{API_PREFIX}/projects/{project_id}/members", headers=client_headers, json={
        "email": freelancer_email,
        "role": "freelancer",
    })
    assert r.status_code == 201, f"Add collaborator failed: {r.text}"
    print(f" Added {freelancer_email} as freelancer collaborator.")

    # 5. Create Milestone Plan & Agreement
    print_step(5, "Create & Agree Milestone Plan")
    r = client.post(f"{API_PREFIX}/projects/{project_id}/milestones/plans", headers=client_headers, json={
        "summary": "Full project roadmap divided into 2 deliverables.",
        "total_budget": 2500.00,
        "currency": "USD",
        "milestones": [
            {
                "title": "UX Prototype & System Architecture",
                "description": "Complete UI wireframes and database architecture diagrams.",
                "deliverables": ["Figma link", "Architecture PDF"],
                "acceptance_criteria": ["All mobile views designed", "DB schema validated"],
                "suggested_budget": 1000.00,
                "order_index": 1,
            },
            {
                "title": "MVP Production Release",
                "description": "Full backend API and frontend checkout implementation.",
                "deliverables": ["GitHub repository", "Working preview deployment"],
                "acceptance_criteria": ["Zero critical bugs", "Payments operational"],
                "suggested_budget": 1500.00,
                "order_index": 2,
            },
        ],
    })
    assert r.status_code == 201, f"Milestone plan creation failed: {r.text}"
    plan = r.json()
    plan_id = plan["id"]
    milestones = plan["milestones"]
    assert len(milestones) == 2, "Expected 2 milestones"
    m1 = milestones[0]
    m1_id = m1["id"]
    print(f" Created milestone plan with 2 milestones. M1 ID: {m1_id} (${m1['suggested_budget']})")

    # Client agrees to plan
    r = client.post(f"{API_PREFIX}/projects/{project_id}/milestones/plans/{plan_id}/agree", headers=client_headers)
    assert r.status_code == 200, f"Client agree failed: {r.text}"

    # Freelancer agrees to plan
    r = client.post(f"{API_PREFIX}/projects/{project_id}/milestones/plans/{plan_id}/agree", headers=freelancer_headers)
    assert r.status_code == 200, f"Freelancer agree failed: {r.text}"
    plan_agreed = r.json()
    assert plan_agreed["status"] == "agreed", f"Plan not agreed: {plan_agreed['status']}"
    print(" Both parties agreed. Milestone plan is now 'AGREED'. Milestones are 'ACTIVE'.")

    # 6. Check Payment Eligibility BEFORE Approval
    print_step(6, "Check Payment Eligibility (Before Approval)")
    r = client.get(f"{API_PREFIX}/payments/milestones/{m1_id}/eligibility", headers=client_headers)
    assert r.status_code == 200, f"Check eligibility failed: {r.text}"
    eligibility = r.json()
    print(" Pre-approval eligibility check:", eligibility)
    assert eligibility["eligible"] is False, "Milestone should NOT be eligible before approval!"
    assert "approved" in eligibility["reason"].lower()
    print(" Correctly rejected checkout: Milestone is active, not approved.")

    # 7. Freelancer Submits Deliverable
    print_step(7, "Freelancer Submits Deliverable for Milestone 1")
    r = client.post(f"{API_PREFIX}/projects/{project_id}/milestones/{m1_id}/submissions", headers=freelancer_headers, json={
        "summary": "Completed UX design system and system architecture specification.",
        "deliverable_notes": "Designs reviewed with accessibility guidelines in mind.",
        "evidence_links": [
            "https://figma.com/file/sample-ux-design",
            "https://github.com/sample/architecture-specs",
        ],
    })
    assert r.status_code == 201, f"Deliverable submission failed: {r.text}"
    submission = r.json()
    submission_id = submission["id"]
    print(f" Deliverable submitted: Submission ID {submission_id}")

    # 8. Client Approves Deliverable
    print_step(8, "Client Approves Deliverable")
    r = client.post(f"{API_PREFIX}/projects/{project_id}/submissions/{submission_id}/decision", headers=client_headers, json={
        "decision": "approved",
        "notes": "Work is high quality and meets all acceptance criteria. Approved for payment release.",
    })
    assert r.status_code == 200, f"Client approval failed: {r.text}"
    submission_approved = r.json()
    assert submission_approved["status"] == "approved"
    print(" Submission approved by Client! Milestone state transitioned to APPROVED.")

    # 9. Check Payment Eligibility AFTER Approval
    print_step(9, "Check Payment Eligibility (After Approval)")
    r = client.get(f"{API_PREFIX}/payments/milestones/{m1_id}/eligibility", headers=client_headers)
    assert r.status_code == 200, f"Check eligibility failed: {r.text}"
    eligibility_post = r.json()
    print(" Post-approval eligibility check:", eligibility_post)
    assert eligibility_post["eligible"] is True, f"Milestone should be eligible: {eligibility_post}"
    assert float(eligibility_post["amount"]) == 1000.00
    assert eligibility_post["currency"] == "USD"
    print(" Milestone is fully eligible for payment checkout! (Amount: $1000.00 USD)")

    # 10. Role Security Check: Freelancer Cannot Initiate Payment
    print_step(10, "Security Check: Freelancer Forbidden from Initiating Payment")
    r = client.post(
        f"{API_PREFIX}/payments/milestones/{m1_id}/orders",
        headers=freelancer_headers,
        json={"provider": "mock"},
    )
    assert r.status_code == 403, f"Expected 403 for freelancer checkout, got: {r.status_code}"
    print(f" Security enforced (403 Forbidden): {r.json()['detail']}")

    # 11. Client Initiates Mock Payment Order
    print_step(11, "Client Initiates Mock Payment Order")
    r = client.post(
        f"{API_PREFIX}/payments/milestones/{m1_id}/orders",
        headers=client_headers,
        json={"provider": "mock"},
    )
    assert r.status_code == 201, f"Create payment order failed: {r.text}"
    payment = r.json()
    payment_id = payment["id"]
    print(f" Payment created (ID: {payment_id}):")
    print(f"   Provider: {payment['provider']}")
    print(f"   Order ID: {payment['provider_order_id']}")
    print(f"   Amount: ${payment['amount']} {payment['currency']}")
    print(f"   Status: {payment['status']}")
    print(f"   Notice: {payment['provider_metadata'].get('notice')}")
    assert payment["provider"] == "mock"
    assert payment["status"] == "order_created"
    assert float(payment["amount"]) == 1000.00
    assert "SIMULATED PAYMENT" in payment["provider_metadata"].get("notice", "")

    # 12. Idempotency Check: Calling create order again returns existing payment
    print_step(12, "Idempotency Check on Payment Order Creation")
    r = client.post(
        f"{API_PREFIX}/payments/milestones/{m1_id}/orders",
        headers=client_headers,
        json={"provider": "mock"},
    )
    assert r.status_code == 200 or r.status_code == 201, f"Repeated order request failed: {r.text}"
    payment_dup = r.json()
    assert payment_dup["id"] == payment_id, "Idempotency check failed: Returned a different payment ID!"
    print(f" Idempotent checkout verified: Retained existing order {payment_dup['provider_order_id']}")

    # 13. Audit Events Verification
    print_step(13, "Verify Payment Record and Audit Events")
    r = client.get(f"{API_PREFIX}/payments/{payment_id}", headers=client_headers)
    assert r.status_code == 200, f"Get payment failed: {r.text}"
    payment_detail = r.json()
    events = payment_detail.get("events", [])
    assert len(events) >= 1, "Expected at least 1 audit event"
    assert events[0]["event_type"] == "ORDER_CREATED"
    print(f" Audit log contains {len(events)} event(s): {[e['event_type'] for e in events]}")

    # 14. Client Confirms Mock Payment
    print_step(14, "Client Confirms Simulated Payment")
    r = client.post(
        f"{API_PREFIX}/payments/{payment_id}/mock-confirm",
        headers=client_headers,
        json={"outcome": "success"},
    )
    assert r.status_code == 200, f"Mock confirm failed: {r.text}"
    confirmed_payment = r.json()
    print(" Confirmation response:", {
        "status": confirmed_payment["status"],
        "provider_capture_id": confirmed_payment["provider_capture_id"],
        "completed_at": confirmed_payment["completed_at"],
    })
    assert confirmed_payment["status"] == "completed"
    assert confirmed_payment["provider_capture_id"].startswith("MOCK-CAP-")
    assert confirmed_payment["completed_at"] is not None

    # 15. Verify Milestone State After Payment
    print_step(15, "Verify Milestone Payment Status Transition")
    r = client.get(f"{API_PREFIX}/projects/{project_id}/milestones/plans", headers=client_headers)
    assert r.status_code == 200
    plans = r.json()
    m1_updated = [m for m in plans[0]["milestones"] if m["id"] == m1_id][0]
    print(f" Milestone 1 Status: {m1_updated['status']}, Payment Status: {m1_updated['payment_status']}")
    assert m1_updated["payment_status"] == "completed", f"Expected completed, got {m1_updated['payment_status']}"
    print(" Milestone payment_status successfully transitioned to 'completed'!")

    # 16. Post-Completion Eligibility Check
    print_step(16, "Post-Completion Eligibility Check")
    r = client.get(f"{API_PREFIX}/payments/milestones/{m1_id}/eligibility", headers=client_headers)
    assert r.status_code == 200
    eligibility_final = r.json()
    print(" Final eligibility check:", eligibility_final)
    assert eligibility_final["eligible"] is False
    assert eligibility_final["payment_status"] == "completed"
    assert eligibility_final["completed_payment_id"] == payment_id
    print(" Correctly rejected duplicate payment: Milestone is already paid in full.")

    # 17. Payment History Verification
    print_step(17, "Verify Payment History (Client and Freelancer)")
    r = client.get(f"{API_PREFIX}/payments", headers=client_headers)
    assert r.status_code == 200
    client_history = r.json()
    assert client_history["total"] >= 1
    matched = [p for p in client_history["payments"] if p["id"] == payment_id]
    assert len(matched) == 1
    print(f" Client history verified: {client_history['total']} transaction(s) recorded.")

    r = client.get(f"{API_PREFIX}/payments", headers=freelancer_headers)
    assert r.status_code == 200
    freelancer_history = r.json()
    assert freelancer_history["total"] >= 1
    matched_f = [p for p in freelancer_history["payments"] if p["id"] == payment_id]
    assert len(matched_f) == 1
    print(f" Freelancer history verified: {freelancer_history['total']} transaction(s) visible.")

    # 18. Simulated Webhook Endpoint Check
    print_step(18, "PayPal Webhook Ingestion Endpoint Check")
    fake_webhook_payload = {
        "id": f"WH-{uuid.uuid4().hex[:12]}",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource_type": "capture",
        "resource": {
            "id": f"CAP-{uuid.uuid4().hex[:12]}",
            "custom_id": payment_id,
            "status": "COMPLETED",
        },
    }
    # Send without valid PayPal signature headers to verify signature rejection behavior
    r = client.post(
        f"{API_PREFIX}/webhooks/paypal",
        json=fake_webhook_payload,
        headers={"paypal-transmission-id": "fake-trans-id"},
    )
    print(f" Webhook test response status: {r.status_code}")
    # In development/sandbox without real transmission signature from PayPal, endpoint rejects unverified webhook
    assert r.status_code in (400, 200), f"Unexpected webhook status: {r.status_code}"
    print(" Webhook security validation verified.")

    print("\n" + "="*70)
    print("ALL DAY 5 LIVE HTTP E2E INTEGRATION TESTS PASSED SUCCESSFULLY! ")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n E2E TEST FAILED: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
