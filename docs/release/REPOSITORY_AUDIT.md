# MilestonePay AI — Repository & Architecture Audit

**Audit Date:** November 9, 2026  
**Auditor:** Principal Full-Stack & DevOps Engineer  
**Repository:** `milestonepay-ai`  
**Current Branch:** `main`  
**Scope:** Frontend (React + TS + Vite), Backend (FastAPI + SQLAlchemy + Alembic), Database (PostgreSQL 16), AI (Google Gemini), Payments (PayPal Sandbox Orders v2 & Capture).

---

## 1. System Architecture Overview

```
                      +---------------------------------------+
                      |          Client / Freelancer          |
                      |   Mobile & Desktop Web Browsers       |
                      +---------------------------------------+
                                          |
                      +---------------------------------------+
                      |       Vercel Edge CDN (Frontend)      |
                      |       React 18 + Vite SPA             |
                      +---------------------------------------+
                                          |
                         REST API Requests (HTTPS / JSON)
                                          v
                      +---------------------------------------+
                      |       Render Web Service (Backend)    |
                      |       FastAPI + Uvicorn ASGI          |
                      +---------------------------------------+
                           /              |              \
                          /               |               \
                         v                v                v
            +----------------+   +----------------+   +----------------+
            |  Managed PG 16 |   |  Google Gemini |   | PayPal Sandbox |
            |  Render DB     |   |  2.5 Flash API |   | REST Orders v2 |
            +----------------+   +----------------+   +----------------+
```

---

## 2. Module Verification & Implementation Status

### A. Authentication & Access Control
- **Endpoints:** `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/me`.
- **Implementation Status:** VERIFIED & PASSING.
- **Password Security:** Passlib with BCrypt hashing (`rounds=12`), zero plaintext storage.
- **Token Security:** PyJWT with HS256, configurable expiration (default 60 minutes), Bearer auth headers.
- **Role Enforcement:** Client and Freelancer roles enforced via `get_current_active_user` and role-specific dependency guards (`require_client_role`, `require_freelancer_role`).
- **Frontend Integration:** `AuthContext` provides persistent token storage, automatic authorization header injection in Axios client, and protected route wrappers.

### B. Project Management
- **Endpoints:** `/api/v1/projects`, `/api/v1/projects/{id}`, `/api/v1/projects/{id}/members`, `/api/v1/projects/{id}/status`.
- **Implementation Status:** VERIFIED & PASSING.
- **Collaborator Pairing:** Strict bilateral membership: one Client and one Freelancer per project workspace.
- **Security Check:** Non-members receive HTTP 403 / 404; duplicate invitations or same-role collaborator additions are rejected.

### C. Gemini AI Milestones & Deliverable Evaluation
- **Services:** `app/services/gemini_service.py`, `app/services/milestone_generator.py`.
- **Implementation Status:** VERIFIED & PASSING.
- **Model:** `gemini-2.5-flash` via official `google-genai` SDK.
- **Capability:** Generates structured milestone plans with exact penny financial totals (100.00% budget allocation), measurable acceptance criteria, timeline estimation, and deliverable validation.
- **Resilience:** Graceful handling of API rate limits, schema validation errors, and timeout protection (60s).

### D. Milestone Workflows & Two-Party Agreement
- **Endpoints:** `/api/v1/projects/{id}/milestone-plans/generate`, `/api/v1/projects/{id}/milestone-plans/manual`, `.../submit-for-approval`, `.../review`.
- **Implementation Status:** VERIFIED & PASSING.
- **Bilateral Approval State Machine:** Plans start in `draft`. Once submitted for approval, both Client and Freelancer must submit an `approved` decision before status transitions to `agreed`.
- **Revisions:** Either party can request revisions with mandatory structured feedback comments.

### E. Deliverable Submission & Evidence Management
- **Endpoints:** `/api/v1/projects/{id}/milestones/{m_id}/submissions`, `/api/v1/submissions/{id}/evidence`, `/api/v1/submissions/{id}/submit`, `/api/v1/submissions/{id}/approve`, `/api/v1/submissions/{id}/request-revision`.
- **Implementation Status:** VERIFIED & PASSING.
- **Upload Constraints:** Max 5 files, 10MB per file; allowed MIME types: PDF, PNG, JPG, ZIP, TXT, MD, DOCX.
- **Storage Architecture:** Local randomized key storage (`backend/uploads/`) with abstracted interface ready for cloud object storage (S3/Cloudinary).
- **Client Decision:** Client review requires either explicit approval (locking milestone for payment) or revision request.

### F. PayPal Sandbox Orders v2 & Payment Settlement
- **Endpoints:** `/api/v1/projects/{id}/milestones/{m_id}/payments`, `/api/v1/payments/{id}/capture`, `/api/v1/payments/{id}/status`, `/api/v1/webhooks/paypal`.
- **Implementation Status:** VERIFIED & LIVE API TESTED.
- **Backend Amount Authority:** Amounts strictly sourced from PostgreSQL milestone row, not client request.
- **Pre-Capture Verification:** Backend checks PayPal `GET /v2/checkout/orders/{id}` before capturing. Blocks capture with HTTP 400 if order is `CREATED` (unapproved), allowing capture only when `APPROVED`.
- **Idempotency:** Re-capturing an already `COMPLETED` order returns existing database record idempotently.
- **Live Sandbox Order:** Order `91W21488L6894071S` ($25.00 USD) active on PayPal Sandbox and reconciled with internal payment record `c51ca6d4-87b5-4553-ba4d-c8a9d5895cfa`.

### G. Dashboards, Analytics & Notifications
- **Endpoints:** `/api/v1/analytics/dashboard`, `/api/v1/analytics/payments`, `/api/v1/projects/{id}/activity`, `/api/v1/notifications`.
- **Implementation Status:** VERIFIED & PASSING.
- **Isolation:** Clients and Freelancers receive role-filtered metrics, project activity streams, and actionable notification badges.

### H. Network & Dev Tunnel Connectivity
- **Vite Proxy:** Routes `/api` to backend port 8000.
- **CORS Configuration:** Configured in `backend/app/core/config.py` supporting `localhost:5173`, `127.0.0.1:5173`, and Microsoft Dev Tunnel URLs (`*.devtunnels.ms`).
- **Health Endpoints:** Both `/api/v1/health` and `/api/v1/health/ready` verified.

---

## 3. Discovered Defects & Fixes Applied

| Defect ID | Severity | Component | Root Cause | Resolution | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEF-001** | P1 | Backend Capture | Unapproved PayPal order called `/capture`, triggering PayPal 422 and marking payment `FAILED`. | Added pre-capture query to `GET /v2/checkout/orders/{id}`. If `CREATED`, returns HTTP 400 and preserves `order_created`. | Unit test passing + Live order test verified. |
| **DEF-002** | P1 | Payment Events | Unique constraint on `provider_event_id` violated when `PAYER_APPROVED` event reused `payment.provider_order_id`. | Appended `-APPROVED` suffix to `provider_event_id` for approval events. | Pytest suite passed with 0 constraint errors. |
| **DEF-003** | P1 | Regression Test | `test_day7_regression.py` mocked create and capture but omitted `get_order`, causing live 404 network call in test. | Added `get_order` mock returning `APPROVED` order status. | `test_day7_regression.py` passed in 3.33s. |
| **DEF-004** | P2 | Frontend UI | Frontend build failed due to strict TS2367 comparison narrowing in `PayPalCheckout.tsx`. | Simplified condition to check `data.internal_status === 'completed'`. | `npx tsc -b` succeeded with 0 errors. |
| **DEF-005** | P2 | Alembic CLI | `alembic current` failed on Windows because libpq binary was blocked by AppControl policy. | Injected `PSYCOPG_IMPL=python` and portable libpq path into `alembic/env.py`. | `alembic current` and `alembic check` both pass cleanly. |
| **DEF-006** | P2 | Terminology | UI and prompts referenced "escrow", inconsistent with standard PayPal checkout model. | Replaced all references with "Milestone Payment", "PayPal Checkout", "Capture Payment". | Grep audit confirmed zero customer-facing escrow terms. |
