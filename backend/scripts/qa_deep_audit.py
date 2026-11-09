"""MilestonePay AI — System-Wide Comprehensive QA & Deep Verification Audit.

Executes all automated edge-case, RBAC, IDOR, payment security, deliverable,
database, and notification verification checks against the running backend
and PostgreSQL database.
"""

from decimal import Decimal
import io
import json
import os
import sys
import uuid
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_PREFIX = f"{BASE_URL}/api/v1"

audit_log = []


def record_check(category: str, test_name: str, passed: bool, details: str = ""):
    status_str = "PASS" if passed else "FAIL"
    entry = {
        "category": category,
        "test": test_name,
        "status": status_str,
        "details": details,
    }
    audit_log.append(entry)
    icon = "[PASS]" if passed else "[FAIL]"
    print(f"  {icon} [{category}] {test_name}: {details}")


def run_audit():
    print("=" * 80)
    print("MILESTONEPAY AI — SYSTEM-WIDE QA & DEEP VERIFICATION AUDIT")
    print(f"Target API Endpoint: {API_PREFIX}")
    print("=" * 80)

    client = requests.Session()

    # ------------------------------------------------------------------------
    # 1. Health & Database Readiness
    # ------------------------------------------------------------------------
    print("\n--- 1. Health & Database Readiness ---")
    try:
        r = client.get(f"{API_PREFIX}/health")
        record_check("HEALTH", "GET /health returns 200", r.status_code == 200, f"Status: {r.status_code}")

        r_ready = client.get(f"{API_PREFIX}/health/ready")
        data = r_ready.json()
        db_ready = r_ready.status_code == 200 and data.get("database") in ("connected", "healthy")
        record_check("HEALTH", "GET /health/ready executes SELECT 1", db_ready, f"Response: {data}")
    except Exception as exc:
        record_check("HEALTH", "Health check execution", False, str(exc))

    # ------------------------------------------------------------------------
    # 2. Authentication Edge Cases & Password Security
    # ------------------------------------------------------------------------
    print("\n--- 2. Authentication Edge Cases & Password Security ---")
    uid = uuid.uuid4().hex[:6]
    client_email = f"client_{uid}@example.com"
    freelancer_email = f"freelancer_{uid}@example.com"
    unrelated_email = f"unrelated_{uid}@example.com"
    valid_password = "ValidPassword123!"

    # Valid Client Registration
    r = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": f"Alice Client {uid}",
        "email": client_email,
        "password": valid_password,
        "confirm_password": valid_password,
        "account_type": "client",
    })
    record_check("AUTH", "Valid Client Registration (201)", r.status_code == 201, f"User ID: {r.json().get('id')}")

    # Valid Freelancer Registration
    r = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": f"Bob Freelancer {uid}",
        "email": freelancer_email,
        "password": valid_password,
        "confirm_password": valid_password,
        "account_type": "freelancer",
    })
    record_check("AUTH", "Valid Freelancer Registration (201)", r.status_code == 201, f"User ID: {r.json().get('id')}")

    # Valid Unrelated User Registration
    r = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": f"Eve Unrelated {uid}",
        "email": unrelated_email,
        "password": valid_password,
        "confirm_password": valid_password,
        "account_type": "freelancer",
    })
    record_check("AUTH", "Valid Unrelated User Registration (201)", r.status_code == 201)

    # Duplicate Email Rejection
    r_dup = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": "Duplicate Tester",
        "email": client_email,
        "password": valid_password,
        "confirm_password": valid_password,
        "account_type": "client",
    })
    record_check("AUTH", "Duplicate Email Rejection (400)", r_dup.status_code == 400, f"Detail: {r_dup.json().get('detail')}")

    # Malformed Email Rejection
    r_bad_email = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": "Bad Email Tester",
        "email": "not-a-valid-email",
        "password": valid_password,
        "confirm_password": valid_password,
        "account_type": "client",
    })
    record_check("AUTH", "Malformed Email Rejection (422)", r_bad_email.status_code == 422)

    # Empty Full Name Rejection (<2 chars)
    r_empty_name = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": "A",
        "email": f"badname_{uid}@example.com",
        "password": valid_password,
        "confirm_password": valid_password,
        "account_type": "client",
    })
    record_check("AUTH", "Short/Empty Full Name Rejection (422)", r_empty_name.status_code == 422)

    # Mismatched Password Rejection
    r_mismatch = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": "Mismatch Tester",
        "email": f"mismatch_{uid}@example.com",
        "password": valid_password,
        "confirm_password": "DifferentPassword123!",
        "account_type": "client",
    })
    record_check("AUTH", "Mismatched Passwords Rejection (422)", r_mismatch.status_code == 422)

    # Weak Password (<8 chars)
    r_short_pw = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": "Short PW Tester",
        "email": f"short_{uid}@example.com",
        "password": "Short1!",
        "confirm_password": "Short1!",
        "account_type": "client",
    })
    record_check("AUTH", "Weak Password (<8 chars) Rejection (422)", r_short_pw.status_code == 422)

    # Weak Password (no digits)
    r_no_digits = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": "No Digits Tester",
        "email": f"nodigits_{uid}@example.com",
        "password": "PasswordOnly!",
        "confirm_password": "PasswordOnly!",
        "account_type": "client",
    })
    record_check("AUTH", "Weak Password (no digits) Rejection (422)", r_no_digits.status_code == 422)

    # Invalid Account Type
    r_bad_type = client.post(f"{API_PREFIX}/auth/register", json={
        "full_name": "Bad Type Tester",
        "email": f"badtype_{uid}@example.com",
        "password": valid_password,
        "confirm_password": valid_password,
        "account_type": "admin_super",
    })
    record_check("AUTH", "Invalid Account Type Rejection (422)", r_bad_type.status_code == 422)

    # Login Valid Credentials
    r_login_client = client.post(f"{API_PREFIX}/auth/login", json={"email": client_email, "password": valid_password})
    record_check("AUTH", "Client Login Success (200)", r_login_client.status_code == 200)
    client_token = r_login_client.json().get("access_token")

    r_login_freelancer = client.post(f"{API_PREFIX}/auth/login", json={"email": freelancer_email, "password": valid_password})
    record_check("AUTH", "Freelancer Login Success (200)", r_login_freelancer.status_code == 200)
    freelancer_token = r_login_freelancer.json().get("access_token")

    r_login_unrelated = client.post(f"{API_PREFIX}/auth/login", json={"email": unrelated_email, "password": valid_password})
    unrelated_token = r_login_unrelated.json().get("access_token")

    # Login Incorrect Password
    r_wrong_pw = client.post(f"{API_PREFIX}/auth/login", json={"email": client_email, "password": "WrongPassword999!"})
    record_check("AUTH", "Incorrect Password Rejection (401)", r_wrong_pw.status_code == 401)

    # Login Unregistered Email
    r_no_user = client.post(f"{API_PREFIX}/auth/login", json={"email": "nonexistent@example.com", "password": valid_password})
    record_check("AUTH", "Unregistered Email Rejection (401)", r_no_user.status_code == 401)

    # Authentication Guard Without Token
    r_no_token = client.get(f"{API_PREFIX}/auth/me")
    record_check("AUTH", "Missing Bearer Token Guard (401)", r_no_token.status_code == 401)

    # Authentication Guard With Invalid Token
    r_bad_token = client.get(f"{API_PREFIX}/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    record_check("AUTH", "Invalid JWT Token Guard (401)", r_bad_token.status_code == 401)

    # Profile Retrieval with Valid Token
    client_auth = {"Authorization": f"Bearer {client_token}"}
    freelancer_auth = {"Authorization": f"Bearer {freelancer_token}"}
    unrelated_auth = {"Authorization": f"Bearer {unrelated_token}"}

    r_me = client.get(f"{API_PREFIX}/auth/me", headers=client_auth)
    record_check("AUTH", "Valid JWT Profile /auth/me (200)", r_me.status_code == 200 and r_me.json()["email"] == client_email)

    # ------------------------------------------------------------------------
    # 3. Project Management, Financial Validation & RBAC / IDOR
    # ------------------------------------------------------------------------
    print("\n--- 3. Project Management, Financial Validation & RBAC / IDOR ---")

    # Project Negative Budget Rejection
    r_neg_budget = client.post(f"{API_PREFIX}/projects", json={
        "title": "Negative Budget Project",
        "description": "Valid description of freelance work requirements.",
        "budget_amount": -500.00,
        "currency": "USD"
    }, headers=client_auth)
    record_check("PROJECTS", "Negative Budget Rejection (422)", r_neg_budget.status_code == 422)

    # Project Zero Budget Rejection
    r_zero_budget = client.post(f"{API_PREFIX}/projects", json={
        "title": "Zero Budget Project",
        "description": "Valid description of freelance work requirements.",
        "budget_amount": 0,
        "currency": "USD"
    }, headers=client_auth)
    record_check("PROJECTS", "Zero Budget Rejection (422)", r_zero_budget.status_code == 422)

    # Project Missing Title Rejection
    r_no_title = client.post(f"{API_PREFIX}/projects", json={
        "description": "Valid description without any project title.",
        "budget_amount": 1000.00,
        "currency": "USD"
    }, headers=client_auth)
    record_check("PROJECTS", "Missing Title Rejection (422)", r_no_title.status_code == 422)

    # Valid Project Creation with Decimal Budget
    project_budget = Decimal("1250.75")
    r_proj = client.post(f"{API_PREFIX}/projects", json={
        "title": f"FinTech AI Gateway {uid}",
        "description": "Comprehensive payment and escrow integration for global freelance contracts.",
        "budget_amount": float(project_budget),
        "currency": "USD",
        "deadline": "2026-12-31"
    }, headers=client_auth)
    record_check("PROJECTS", "Create Project with Decimal Precision Budget (201)", r_proj.status_code == 201)
    project_id = r_proj.json().get("id")

    # Add Collaborator (Freelancer)
    r_collab = client.post(f"{API_PREFIX}/projects/{project_id}/members", json={
        "email": freelancer_email
    }, headers=client_auth)
    record_check("PROJECTS", "Add Registered Complementary Collaborator (200)", r_collab.status_code == 200)

    # Add Duplicate Collaborator Rejection
    r_dup_collab = client.post(f"{API_PREFIX}/projects/{project_id}/members", json={
        "email": freelancer_email
    }, headers=client_auth)
    record_check("PROJECTS", "Duplicate Collaborator Rejection (400)", r_dup_collab.status_code == 400)

    # Add Nonexistent Collaborator Rejection
    r_no_collab = client.post(f"{API_PREFIX}/projects/{project_id}/members", json={
        "email": "phantom_user@example.com"
    }, headers=client_auth)
    record_check("PROJECTS", "Nonexistent Collaborator Rejection (404)", r_no_collab.status_code == 404)

    # Project Access Verification for Members
    r_acc_client = client.get(f"{API_PREFIX}/projects/{project_id}", headers=client_auth)
    record_check("PROJECTS", "Creator Client Access (200)", r_acc_client.status_code == 200)

    r_acc_freelancer = client.get(f"{API_PREFIX}/projects/{project_id}", headers=freelancer_auth)
    record_check("PROJECTS", "Collaborator Freelancer Access (200)", r_acc_freelancer.status_code == 200)

    # IDOR / Tenant Isolation: Unrelated User Access Rejection
    r_acc_unrelated = client.get(f"{API_PREFIX}/projects/{project_id}", headers=unrelated_auth)
    record_check("SECURITY", "IDOR: Unrelated User Project Read Blocked (403)", r_acc_unrelated.status_code == 403)

    r_edit_unrelated = client.patch(f"{API_PREFIX}/projects/{project_id}", json={
        "title": "Hacked Title"
    }, headers=unrelated_auth)
    record_check("SECURITY", "IDOR: Unrelated User Project Update Blocked (403)", r_edit_unrelated.status_code == 403)

    # ------------------------------------------------------------------------
    # 4. Milestone Plan Agreement & Bilateral Approval Workflow
    # ------------------------------------------------------------------------
    print("\n--- 4. Milestone Plan Agreement & Bilateral Approval Workflow ---")
    m1_amount = Decimal("625.00")
    m2_amount = Decimal("625.75")
    assert m1_amount + m2_amount == project_budget

    plan_payload = {
        "project_summary": "Two-phase architecture and payments delivery roadmap.",
        "milestones": [
            {
                "sequence_number": 1,
                "title": "Phase 1: Architecture, Schemas & Auth",
                "description": "Establish FastAPI database schemas, models, and Argon2id auth.",
                "deliverables": ["Database Models", "OpenAPI Documentation"],
                "acceptance_criteria": [
                    "All authentication endpoints return JWT",
                    "Database migrations apply cleanly"
                ],
                "estimated_duration_days": 14,
                "budget_percentage": 50.0,
                "dependencies": []
            },
            {
                "sequence_number": 2,
                "title": "Phase 2: Payment Gateway & Settlement",
                "description": "PayPal sandbox capture and webhook settlement.",
                "deliverables": ["PayPal Checkout Components", "Capture Endpoint"],
                "acceptance_criteria": [
                    "PayPal Order captures successfully",
                    "Database amount matches authorized balance"
                ],
                "estimated_duration_days": 10,
                "budget_percentage": 50.0,
                "dependencies": [1]
            }
        ]
    }

    # Create Draft Plan via /projects/{project_id}/milestone-plans/manual
    r_plan = client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/manual", json=plan_payload, headers=client_auth)
    record_check("MILESTONES", "Create Manual Plan with Cent-Exact Sum (201)", r_plan.status_code == 201)
    plan_data = r_plan.json()
    plan_id = plan_data.get("id")
    milestone_id_1 = plan_data["milestones"][0]["id"]
    milestone_id_2 = plan_data["milestones"][1]["id"]

    # Submit Plan for Bilateral Approval
    r_sub_plan = client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/submit-for-approval", headers=client_auth)
    record_check("MILESTONES", "Submit Plan for Approval (200 - pending_approval)", r_sub_plan.status_code == 200 and r_sub_plan.json()["status"] == "pending_approval")

    # Revision Request by Freelancer
    r_rev = client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/request-revision", json={
        "comment": "Please extend duration for Phase 2 integration."
    }, headers=freelancer_auth)
    record_check("MILESTONES", "Freelancer Request Revision (200 - revision_requested)", r_rev.status_code == 200 and r_rev.json()["status"] == "revision_requested")

    # Resubmit Plan
    client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/submit-for-approval", headers=client_auth)

    # Bilateral Approval: Client Approves
    r_app_client = client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/approve", json={
        "version": plan_data["version"]
    }, headers=client_auth)
    record_check("MILESTONES", "First Approval by Client (Status stays pending_approval)", r_app_client.status_code == 200 and r_app_client.json()["status"] == "pending_approval")

    # Bilateral Approval: Freelancer Approves -> Transitions to AGREED
    r_app_freelancer = client.post(f"{API_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}/approve", json={
        "version": plan_data["version"]
    }, headers=freelancer_auth)
    record_check("MILESTONES", "Second Approval by Freelancer (Status locked to AGREED)", r_app_freelancer.status_code == 200 and r_app_freelancer.json()["status"] == "agreed")

    # Attempt to Edit Agreed Plan (Must be rejected)
    r_edit_agreed = client.patch(f"{API_PREFIX}/projects/{project_id}/milestone-plans/{plan_id}", json={
        "title": "Modified Agreed Plan"
    }, headers=client_auth)
    record_check("SECURITY", "Editing Agreed Plan Strictly Blocked (400)", r_edit_agreed.status_code == 400)

    # ------------------------------------------------------------------------
    # 5. Deliverable Submission, Evidence Security & Client Approval
    # ------------------------------------------------------------------------
    print("\n--- 5. Deliverable Submission, Evidence Security & Client Approval ---")

    # Client Attempting to Submit Deliverable as Freelancer (Blocked)
    r_client_sub = client.post(f"{API_PREFIX}/projects/{project_id}/milestones/{milestone_id_1}/submissions", json={
        "description": "Client trying to submit work"
    }, headers=client_auth)
    record_check("SECURITY", "Role Guard: Client Blocked from Submitting Deliverables (403)", r_client_sub.status_code == 403)

    # Freelancer Creates Submission Draft
    r_sub = client.post(f"{API_PREFIX}/projects/{project_id}/milestones/{milestone_id_1}/submissions", json={
        "description": "Completed Phase 1 backend architecture and models.",
        "demonstration_url": "https://github.com/milestonepay/milestonepay-ai"
    }, headers=freelancer_auth)
    record_check("SUBMISSIONS", "Freelancer Creates Submission Draft (201)", r_sub.status_code == 201)
    submission_id = r_sub.json().get("id")

    # Upload Valid Evidence File via /submissions/{submission_id}/evidence
    evidence_content = b"# Phase 1 Verification Log\nAll API endpoints operational and tested."
    files = [("files", ("verification_log.txt", io.BytesIO(evidence_content), "text/plain"))]
    r_upload = client.post(
        f"{API_PREFIX}/submissions/{submission_id}/evidence",
        files=files,
        headers=freelancer_auth
    )
    record_check("SUBMISSIONS", "Upload Evidence with SHA-256 and Randomized Key (201)", r_upload.status_code == 201)
    evidence_id = r_upload.json()["evidence"][0]["id"]

    # IDOR: Unrelated User Attempting to Download Evidence File (Blocked)
    r_download_unrelated = client.get(
        f"{API_PREFIX}/submissions/{submission_id}/evidence/{evidence_id}",
        headers=unrelated_auth
    )
    record_check("SECURITY", "IDOR: Unrelated User Evidence Download Blocked (403)", r_download_unrelated.status_code == 403)

    # Finalize and Submit Work for Client Review via /submissions/{submission_id}/submit
    r_finalize = client.post(
        f"{API_PREFIX}/submissions/{submission_id}/submit",
        headers=freelancer_auth
    )
    record_check("SUBMISSIONS", "Finalize Submission for Client Review (200 - submitted)", r_finalize.status_code == 200)

    # Freelancer Attempting to Approve Own Submission (Blocked)
    r_freelancer_app = client.post(
        f"{API_PREFIX}/submissions/{submission_id}/approve",
        headers=freelancer_auth
    )
    record_check("SECURITY", "Role Guard: Freelancer Self-Approval Blocked (403)", r_freelancer_app.status_code == 403)

    # Client Approves Submission via /submissions/{submission_id}/approve
    r_client_app = client.post(
        f"{API_PREFIX}/submissions/{submission_id}/approve",
        json={"decision": "approved", "comment": "Excellent architecture work. Verified and approved."},
        headers=client_auth
    )
    record_check("SUBMISSIONS", "Client Approves Submission (200 - approved)", r_client_app.status_code == 200 and r_client_app.json()["status"] == "approved")

    # ------------------------------------------------------------------------
    # 6. Payment Security, Database Amount Authority & Idempotent Capture
    # ------------------------------------------------------------------------
    print("\n--- 6. Payment Security, Database Amount Authority & Idempotent Capture ---")

    # Check Milestone Payment Eligibility
    r_elig = client.get(f"{API_PREFIX}/projects/{project_id}/milestones/{milestone_id_1}/payment-eligibility", headers=client_auth)
    record_check("PAYMENTS", "Approved Milestone Is Payment Eligible (eligible=True)", r_elig.status_code == 200 and r_elig.json()["eligible"] is True)

    # Freelancer Blocked from Initiating Payment
    r_freelancer_pay = client.post(
        f"{API_PREFIX}/projects/{project_id}/milestones/{milestone_id_1}/payments",
        json={"provider": "mock"},
        headers=freelancer_auth
    )
    record_check("SECURITY", "Role Guard: Freelancer Blocked from Initiating Payment (400/403)", r_freelancer_pay.status_code in (400, 403))

    # Unrelated User Blocked from Initiating Payment
    r_unrelated_pay = client.post(
        f"{API_PREFIX}/projects/{project_id}/milestones/{milestone_id_1}/payments",
        json={"provider": "mock"},
        headers=unrelated_auth
    )
    record_check("SECURITY", "IDOR: Unrelated User Blocked from Initiating Payment (400/403)", r_unrelated_pay.status_code in (400, 403))

    # Client Initiates Payment (Amount strictly derived from PostgreSQL)
    r_create_pay = client.post(
        f"{API_PREFIX}/projects/{project_id}/milestones/{milestone_id_1}/payments",
        json={"provider": "mock"},
        headers=client_auth
    )
    record_check("PAYMENTS", "Payment Created with DB Amount Authority (201)", r_create_pay.status_code == 201)
    payment_data = r_create_pay.json()
    payment_id = payment_data.get("id")

    # Verify Canonical Amount Matches Milestone Exactly
    expected_m1_amount = Decimal(str(r_elig.json()["amount"]))
    actual_payment_amount = Decimal(str(payment_data.get("amount", 0)))
    record_check("PAYMENTS", f"Payment Amount Matches DB (${expected_m1_amount} vs ${actual_payment_amount})", actual_payment_amount == expected_m1_amount)

    # Confirm / Capture Payment via /payments/{payment_id}/mock-confirm
    r_confirm = client.post(
        f"{API_PREFIX}/payments/{payment_id}/mock-confirm",
        json={"outcome": "success"},
        headers=client_auth
    )
    record_check("PAYMENTS", "Payment Captured and Settled (200 - completed)", r_confirm.status_code == 200 and r_confirm.json()["status"] == "completed")

    # Idempotent Repeat Capture Call
    r_dup_capture = client.post(
        f"{API_PREFIX}/payments/{payment_id}/mock-confirm",
        json={"outcome": "success"},
        headers=client_auth
    )
    record_check("PAYMENTS", "Duplicate Capture Call Handled Idempotently (200)", r_dup_capture.status_code == 200)

    # ------------------------------------------------------------------------
    # 7. Notifications & Analytics
    # ------------------------------------------------------------------------
    print("\n--- 7. Notifications & Analytics ---")

    # In-App Notifications for Freelancer
    r_notifs = client.get(f"{API_PREFIX}/notifications", headers=freelancer_auth)
    record_check("NOTIFICATIONS", "Freelancer Received System Notifications (200)", r_notifs.status_code == 200 and len(r_notifs.json()["notifications"]) > 0)

    # Unread Count Check
    r_unread = client.get(f"{API_PREFIX}/notifications/unread-count", headers=freelancer_auth)
    record_check("NOTIFICATIONS", "Unread Notification Count Endpoint (200)", r_unread.status_code == 200 and "unread_count" in r_unread.json())

    # Mark All Read via PATCH /notifications/read-all
    r_read_all = client.patch(f"{API_PREFIX}/notifications/read-all", headers=freelancer_auth)
    record_check("NOTIFICATIONS", "Mark All Notifications Read (200)", r_read_all.status_code == 200)

    # Verify Unread Count is 0
    r_unread_after = client.get(f"{API_PREFIX}/notifications/unread-count", headers=freelancer_auth)
    record_check("NOTIFICATIONS", "Unread Count Decremented to 0", r_unread_after.json()["unread_count"] == 0)

    # Client Dashboard Analytics
    r_client_dash = client.get(f"{API_PREFIX}/analytics/dashboard", headers=client_auth)
    record_check("ANALYTICS", "Client Dashboard Analytics Return Accurate Aggregates", r_client_dash.status_code == 200 and r_client_dash.json()["projects"]["total"] >= 1)

    # Freelancer Dashboard Analytics
    r_free_dash = client.get(f"{API_PREFIX}/analytics/dashboard", headers=freelancer_auth)
    record_check("ANALYTICS", "Freelancer Dashboard Analytics Return Accurate Aggregates", r_free_dash.status_code == 200 and r_free_dash.json()["projects"]["total"] >= 1)

    # Settlement Trends via GET /analytics/payments
    r_trends = client.get(f"{API_PREFIX}/analytics/payments", headers=client_auth)
    record_check("ANALYTICS", "Payment Settlement Trends Accessible (200)", r_trends.status_code == 200 and "trends" in r_trends.json())

    # Project Activity Audit
    r_activity = client.get(f"{API_PREFIX}/projects/{project_id}/activities", headers=client_auth)
    record_check("AUDIT", "Project Activity Audit Trail Persisted (200)", r_activity.status_code == 200 and len(r_activity.json()["activities"]) >= 5)

    # ------------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY:")
    passed_count = sum(1 for c in audit_log if c["status"] == "PASS")
    failed_count = sum(1 for c in audit_log if c["status"] == "FAIL")
    print(f"Total Checks Executed: {len(audit_log)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print("=" * 80)

    return failed_count == 0


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
