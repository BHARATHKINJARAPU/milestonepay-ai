# MilestonePay AI — Judge Testing & Evaluation Guide
**PayPal AI Hackathon Submission**

---

## 1. Executive Summary

**MilestonePay AI** solves the \$1.5 trillion freelance economy's single biggest vulnerability: **ambiguous scopes that trigger delivery disputes and delayed payments**.

By combining **Google Gemini 2.5 Flash** with **PayPal Sandbox Checkout & Capture**, MilestonePay AI turns vague freelance briefs into crystal-clear milestones, evaluates submitted evidence objectively against agreed acceptance criteria, and enables immediate, tamper-proof milestone payments upon client sign-off.

---

## 2. Fast Evaluation Architecture & Endpoints

| Component | Local URL | Default Port | Production Ready Specification |
|---|---|---|---|
| **Frontend UI (React + TS + Tailwind)** | `http://localhost:5173` | 5173 | Vercel SPA (`frontend/vercel.json`) |
| **Backend REST API (FastAPI)** | `http://127.0.0.1:8000` | 8000 | Render Web Service (`render.yaml`) |
| **Interactive OpenAPI Documentation** | `http://127.0.0.1:8000/docs` | 8000 | Swagger UI with OpenAPI 3.1 schema |
| **API Health & DB Readiness** | `http://127.0.0.1:8000/api/v1/health/ready` | 8000 | Synchronous DB ping check |

---

## 3. Recommended Judge Evaluation Walkthrough (10-Minute Guide)

For the most authentic experience, we recommend opening two browser windows side-by-side:
- **Window 1 (Left):** Client Persona
- **Window 2 (Right):** Freelancer Persona

---

### Step 1: Account Creation & Dual-Role Setup
1. Open `http://localhost:5173/register` in Window 1:
   - Select **Client Account**.
   - Fill in:
     - Full Name: `Alice Client`
     - Email: `alice.client@example.com`
     - Password: `Password123!`
   - Click **Create Account** and sign in.
2. Open `http://localhost:5173/register` in an Incognito / Window 2:
   - Select **Freelancer Account**.
   - Fill in:
     - Full Name: `Bob Freelancer`
     - Email: `bob.freelancer@example.com`
     - Password: `Password123!`
   - Click **Create Account** and sign in.

---

### Step 2: Create a Project & Invite Freelancer
*(As Alice Client in Window 1)*
1. Click **+ New Project** in the navigation header.
2. Enter natural-language project details:
   - **Title:** `Cross-Platform FinTech Mobile Wallet`
   - **Description:** 
     > *"We need an intuitive mobile wallet app with biometric login, card tokenization, and instant peer-to-peer transfer. The app must comply with OWASP mobile security standards, include high-fidelity Figma designs, clean React Native code, and complete API integration tests."*
   - **Total Budget:** `$5,000.00`
   - **Currency:** `USD`
3. Click **Create Project**.
4. In the Project Overview page, locate the **Project Collaborators** card:
   - Enter Bob's email: `bob.freelancer@example.com`
   - Role: `Freelancer`
   - Click **Invite Collaborator**.
5. *Instant Verification:* Switch to Window 2 (Bob). Notice the **Notification Bell** updates with an unread badge: `"Invited to Project: You have been added to 'Cross-Platform FinTech Mobile Wallet' as freelancer."`

---

### Step 3: AI Milestone Generation (Google Gemini 2.5)
*(In Window 1 or Window 2 — Milestone Workspace)*
1. Navigate to the project and click **Milestones Workspace**.
2. Click **Generate Milestones with Gemini AI**.
3. (Optional) Provide additional guidance, e.g., *"Break down into 2 distinct milestones prioritizing Figma designs first, then API integration."*
4. Click **Generate Milestone Proposal**:
   - Google Gemini decomposes the unstructured prompt into structured milestones with:
     - Clear titles, scope, and concrete tangible deliverables.
     - Objective, testable acceptance criteria.
     - Estimated timelines (days) and budget allocations totaling exactly 100% ($5,000.00).
5. Click **Submit for Bilateral Review**. The status transitions to `Pending Approval`.

---

### Step 4: Bilateral Mutual Agreement (Two-Party Sign-Off)
To prevent unilateral scope creep, work and payments are locked until **both parties** review and sign off:
1. **Bob (Freelancer, Window 2):** Clicks **Approve Plan Proposal**.
2. **Alice (Client, Window 1):** Clicks **Approve Plan Proposal**.
3. *System Action:* With dual sign-offs recorded, the Milestone Plan transitions to **AGREED**, and the project milestones become **ACTIVE**.

---

### Step 5: Freelancer Work Submission & Evidence Upload
*(As Bob Freelancer in Window 2)*
1. Click on **Milestone #1: UI/UX Architecture & Figma Tokens**.
2. Click **Submit Deliverable Work**:
   - **Description:** *"Completed high-fidelity mobile prototype with 40+ responsive screens, WCAG AAA accessibility, and design token repository."*
   - **Demo URL:** `https://www.figma.com/file/sample-wallet`
   - **Evidence Upload:** Drag and drop or attach evidence files (e.g., sample `.pdf` documentation or `.png` architecture diagram).
3. Click **Submit Work for AI Evaluation**.
4. *System Action:* 
   - Files are validated (whitelist: PDF, PNG, JPG, TXT; 10 MB cap; SHA-256 hashed; stored with randomized UUID keys).
   - Work status transitions to `Submitted`.
   - Google Gemini multimodal evaluation is automatically triggered in the background.

---

### Step 6: AI Deliverable Verification & Audit Report
*(Viewable by both Client & Freelancer)*
1. On the Submission Detail view, inspect the **AI Deliverable Audit Card**:
   - **Evaluation Verdict:** `MET` (or `PARTIALLY_MET`).
   - **Confidence Score:** 92–96%.
   - **Executive Summary:** Synthesized analysis of submitted deliverables against agreed criteria.
   - **Criterion Breakdown:** Detailed status per criteria item (`Passed` / `Attention Needed`).
   - **Key Strengths & Recommended Next Steps**.

---

### Step 7: Client Deliverable Sign-off
*(As Alice Client in Window 1)*
1. Review the freelancer's evidence and the objective AI evaluation report.
2. Select **Approve Deliverable Work**:
   - Optional sign-off notes: *"Excellent work. Deliverables completely fulfill Milestone 1 criteria."*
   - Click **Confirm Approval**.
3. *System Action:* Milestone #1 status transitions to **APPROVED**, unlocking payment eligibility.

---

### Step 8: PayPal Sandbox Payment Checkout & Capture
*(As Alice Client in Window 1)*
1. On Milestone #1, click the **Release Payment ($2,000.00)** button.
2. The **Milestone Payment Checkout** modal displays:
   - Milestone sequence, title, and agreed amount: **$2,000.00 USD**.
   - Payee details: Bob Freelancer (`bob.freelancer@example.com`).
3. Choose the payment provider:
   - **Option A (PayPal Sandbox):**
     - Select **PayPal Sandbox**.
     - Click the official **PayPal Checkout Button** (rendered via `@paypal/react-paypal-js`).
     - Log in with your PayPal Sandbox Personal Buyer credentials:
       - Email: `buyer@personal.example.com` (or your Sandbox Buyer Account)
       - Password: (Sandbox Buyer Password)
     - Click **Pay Now**.
     - The backend securely captures the payment via PayPal REST API v2 (`/v2/checkout/orders/{id}/capture`), strictly verifies that the captured amount matches the database milestone amount, and updates the milestone to `PAID`.
   - **Option B (Simulated Mock Provider - Zero Setup Required):**
     - Select **Development Mock Provider (Simulated Sandbox)**.
     - Click **Simulate Successful Payment**.
     - The backend records a simulated settlement transaction with audit logging.
4. *Immediate Post-Payment Settlement:*
   - You are redirected to the **Payment Receipt / Confirmation Screen**.
   - Bob receives a real-time notification: `"Milestone Payment Released! Payment of USD 2,000.00 has been released by Alice Client."`
   - The Project Activity Timeline records: `"Payment Settled for 'Milestone #1' via PayPal ($2,000.00 USD)."`

---

### Step 9: Analytics & Role-Based Dashboards
1. Navigate to `/dashboard` as **Alice Client**:
   - Total Projects: 1 active.
   - Total Committed Budget: $5,000.00.
   - Settled Payments: $2,000.00.
   - Review Center: Empty (all pending submissions reviewed).
   - Interactive Settlement Trend Chart reflecting the captured payment.
2. Navigate to `/dashboard` as **Bob Freelancer**:
   - Upcoming Milestones: Phase 2 in progress.
   - Realized Earnings: $2,000.00 USD.
   - Pipeline value remaining: $3,000.00 USD.

---

## 4. Security & Robustness Verification Checklist

Judges are encouraged to test negative edge cases to verify application security:

| Security Defense | Test Method | Expected Behavior |
|---|---|---|
| **Amount Tampering** | Inspect browser network tab and attempt to tamper with order amount. | **BLOCKED:** The frontend never sends an amount. The backend queries `milestone.amount` directly from PostgreSQL and rejects discrepancies. |
| **Unauthorized Access** | Try accessing `/projects/{id}` using a non-member account. | **BLOCKED:** Returns HTTP 403 Forbidden / HTTP 404. |
| **Double Capture / Race Conditions** | Attempt to trigger duplicate capture on an already settled payment. | **IDEMPOTENT:** Returns existing completed payment record without duplicate billing. |
| **Malicious File Upload** | Attempt to upload an `.exe` or `.sh` script as evidence. | **BLOCKED:** Returns HTTP 400 with whitelist rejection (PDF, PNG, JPG, TXT only). |
| **Path Traversal Protection** | Attempt to supply `../../etc/passwd` in filename. | **BLOCKED:** Files are assigned random UUID hex keys on server disk. |
| **Bilateral Lock** | Attempt to submit work on a draft milestone plan. | **BLOCKED:** Submissions are forbidden until both parties sign the plan into `AGREED` state. |

---

## 5. Running the Automated Test Suite

MilestonePay AI comes with 100% passing automated test coverage:

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

**Expected Result:**
```
======================= 79 passed, 1 warning in 36.46s =======================
```

To run the live HTTP end-to-end regression script against running backend and database servers:
```bash
cd backend
.\.venv\Scripts\python.exe scripts\verify_day6_live.py
```

**Expected Result:**
```
======================================================================
ALL DAY 6 LIVE HTTP FULL INTEGRATION TESTS PASSED SUCCESSFULLY! 
======================================================================
```

---

## 6. PayPal Hackathon Technology Stack

- **AI Engine:** Google Gemini 2.5 Flash with Pydantic Structured Outputs (`gemini_service.py`)
- **Payment Processing:** PayPal REST API v2 (`/v2/checkout/orders`, `/v2/checkout/orders/{id}/capture`), PayPal Webhooks, and PayPal JavaScript SDK v6
- **Backend Architecture:** Python 3.13, FastAPI, SQLAlchemy 2.0, PostgreSQL 16, Alembic Migrations, Argon2id Passwords, PyJWT
- **Frontend Architecture:** React 19, TypeScript 5.8, Tailwind CSS, Vite, Lucide Icons, Axios Interceptors

