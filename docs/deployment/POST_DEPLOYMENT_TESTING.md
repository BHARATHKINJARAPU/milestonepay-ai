# MilestonePay AI — Post-Deployment Verification & Smoke Testing Guide

This guide provides an end-to-end testing protocol to verify that the deployed Render backend, Render PostgreSQL, and Vercel frontend function correctly together in production.

---

## 1. Automated Health & Smoke Tests (CLI)

Run these checks against your live deployed endpoints (replace `milestonepay-api.onrender.com` with your actual domain):

### Test 1: Root Info Endpoint
```bash
curl -i https://milestonepay-api.onrender.com/
```
**Expected Output:**
```http
HTTP/1.1 200 OK
content-type: application/json

{"app":"MilestonePay AI","version":"0.1.0","docs":"/docs","health":"/api/v1/health","ready":"/api/v1/health/ready"}
```

### Test 2: Basic Liveness Probe
```bash
curl -i https://milestonepay-api.onrender.com/api/v1/health
```
**Expected Output:**
```http
HTTP/1.1 200 OK
{"status":"healthy","service":"milestonepay-api"}
```

### Test 3: Database Readiness Probe
```bash
curl -i https://milestonepay-api.onrender.com/api/v1/health/ready
```
**Expected Output:**
```http
HTTP/1.1 200 OK
{"status":"ready","service":"milestonepay-api","database":"connected"}
```
*(If output shows `status: degraded`, verify the Render PostgreSQL instance is running and `DATABASE_URL` is correct).*

### Test 4: CORS Preflight Verification
```bash
curl -i -X OPTIONS https://milestonepay-api.onrender.com/api/v1/auth/login \
  -H "Origin: https://milestonepay-ai.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```
**Expected Output:**
```http
HTTP/1.1 200 OK
access-control-allow-origin: https://milestonepay-ai.vercel.app
access-control-allow-credentials: true
access-control-allow-methods: *
```

---

## 2. End-to-End Browser Functional Walkthrough

Execute the following test script in your browser on `https://milestonepay-ai.vercel.app`:

### Step 1: User Registration & Authentication
1. Open `https://milestonepay-ai.vercel.app/register` in an incognito window.
2. Register a new Client account:
   - Name: `Production Client`
   - Email: `prod_client@example.com`
   - Role: `Client`
3. Verify automatic redirect to `/dashboard`.
4. Log out and log back in at `/login` to confirm session persistence.

### Step 2: Project Creation
1. Click **+ New Project**.
2. Enter:
   - Title: `Production Cloud Verification Pipeline`
   - Description: `E2E automated testing for cloud-deployed MilestonePay AI on Render and Vercel`
   - Budget: `1000`
   - Currency: `USD`
3. Submit and verify project appears in the project list.

### Step 3: Collaborator Invitation
1. In another private window, register a Freelancer account: `prod_freelancer@example.com`.
2. In the Client window, open the project details and invite `prod_freelancer@example.com`.
3. Switch to the Freelancer window; confirm the project appears in their dashboard and an unread notification badge appears.

### Step 4: AI Milestone Plan Generation (Gemini)
1. In the project workspace, click **Generate with Gemini AI**.
2. Enter project requirements and timeline.
3. Submit and await Gemini response (typically 3–5 seconds).
4. Verify milestones sum to exactly $1,000.00 USD (100.00% budget allocation).
5. Both Client and Freelancer approve the plan; verify plan transitions to `agreed`.

### Step 5: Deliverable Submission & Evidence Upload
1. As the Freelancer, open Milestone #1 and click **Submit Work**.
2. Upload a test PDF or screenshot evidence artifact (< 10MB).
3. Click **Submit Deliverable**.
4. Confirm Gemini AI evaluates the deliverable against the agreed acceptance criteria.

### Step 6: Client Approval & PayPal Sandbox Checkout
1. As the Client, review the AI audit and click **Approve Milestone Work**.
2. Milestone transitions to `approved`.
3. Click **Release Payment**.
4. Select **PayPal Sandbox** and click **Continue to PayPal Sandbox**.
5. Log in with your Personal Sandbox buyer account in the PayPal popup and complete purchase.
6. Click **Check Approval Status**; confirm status updates to `Buyer Approved`.
7. Click **Verify & Capture Payment**.
8. Confirm receipt displays settled amount ($1,000.00 USD) and PayPal Capture ID.

---

## 3. Production Troubleshooting Playbook

| Symptom | Probable Cause | Remediation |
| :--- | :--- | :--- |
| **Network Error on Login/Register** | `VITE_API_BASE_URL` misconfigured in Vercel. | In Vercel, check that `VITE_API_BASE_URL` contains `https://milestonepay-api.onrender.com` without a trailing slash. Redeploy the frontend. |
| **CORS Blocked in Browser** | `CORS_ORIGINS` in Render does not match Vercel URL. | In Render Dashboard, ensure `CORS_ORIGINS` includes your exact Vercel domain (e.g. `https://milestonepay-ai.vercel.app`). |
| **HTTP 502 / Database Error** | `DATABASE_URL` scheme or SSL mode incompatible. | Ensure `DATABASE_URL` uses the Render Internal Database URL. Our backend validator automatically handles `postgresql+psycopg://`. |
| **Alembic Table Missing** | Migrations were not applied on deploy. | In Render Web Service settings, verify build command includes `alembic upgrade head`. Or run migrations manually via PowerShell. |
| **404 on Deep Route Refresh** | Vercel SPA rewrite missing. | Verify `frontend/vercel.json` is present in the repository and contains the rewrite `/(.*) -> /index.html`. |
| **Uploaded Files Disappear** | Render ephemeral filesystem reset on redeploy. | In Render Web Service, attach a **Persistent Disk** mounted at `/var/data/uploads` and set `UPLOAD_DIR=/var/data/uploads`. |
