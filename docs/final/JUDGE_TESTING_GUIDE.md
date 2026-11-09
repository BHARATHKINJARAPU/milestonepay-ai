# MilestonePay AI — Judge Testing & Evaluation Guide
**PayPal AI Hackathon Submission**  
*Document Generated: Day 8 Final Independent Review*

---

## 1. Quick Evaluation Summary

This guide provides hackathon judges with step-by-step instructions for testing MilestonePay AI. You can test the platform either via the **Hosted Demo** or via **Local Quickstart** in your own environment.

### Core Endpoints & Access Points

| Component | Hosted URL | Local URL | Port |
|---|---|---|---|
| **Frontend Application** | `https://milestonepay-ai.vercel.app` | `http://localhost:5173` | 5173 |
| **Backend REST API** | `https://milestonepay-api.onrender.com` | `http://127.0.0.1:8000` | 8000 |
| **Interactive API Documentation** | `/docs` | `http://127.0.0.1:8000/docs` | 8000 |
| **API Health & DB Readiness** | `/api/v1/health/ready` | `http://127.0.0.1:8000/api/v1/health/ready` | 8000 |

---

## 2. Setting Up Test Accounts

MilestonePay AI features strict role separation between **Client** and **Freelancer** accounts. For the best testing experience, we recommend using two browser windows side-by-side:
- **Window 1 (Normal Window):** Client Persona
- **Window 2 (Incognito Window):** Freelancer Persona

### Account Setup (Zero Pre-Existing Secrets Required):
1. **Window 1 (Client):**
   - Go to `http://localhost:5173/register`
   - Select **Client Account**
   - Full Name: `Alice Client`
   - Email: `alice.client@judge-test.com`
   - Password: `Password123!`
   - Click **Create Account** and sign in.
2. **Window 2 (Freelancer):**
   - Go to `http://localhost:5173/register`
   - Select **Freelancer Account**
   - Full Name: `Bob Freelancer`
   - Email: `bob.freelancer@judge-test.com`
   - Password: `Password123!`
   - Click **Create Account** and sign in.

---

## 3. Step-by-Step Judge Walkthrough (10-Minute Guided Tour)

---

### Step 1: Create a Project & Invite Freelancer
*(As Alice Client in Window 1)*
1. Click **+ New Project** in the dashboard header.
2. Enter project details:
   - **Title:** `FinTech Mobile Wallet & PayPal Gateway`
   - **Description:** 
     > *"We need an intuitive cross-platform mobile wallet app with biometric login, transaction history, and instant PayPal checkout. Deliverables must include complete Figma UI designs, clean React Native code, and OpenAPI integration tests."*
   - **Total Budget:** `$4,000.00`
   - **Currency:** `USD`
3. Click **Create Project**.
4. In the Project Overview page, locate **Project Collaborators**:
   - Collaborator Email: `bob.freelancer@judge-test.com`
   - Role: `Freelancer`
   - Click **Invite Collaborator**.
5. *Instant Verification:* Switch to Window 2 (Bob). Notice the **Notification Bell** updates with an unread badge: `"Invited to Project: You have been added to 'FinTech Mobile Wallet & PayPal Gateway' as freelancer."`

---

### Step 2: AI Milestone Generation (Google Gemini 2.5)
*(In Window 1 or Window 2 — Milestone Workspace)*
1. Navigate to the project and click **Milestones Workspace**.
2. Click **Generate Milestones with Gemini AI**.
3. (Optional) Provide additional guidance, e.g., *"Focus Phase 1 on UI/UX and Phase 2 on PayPal integration."*
4. Click **Generate Milestone Proposal**:
   - Google Gemini 2.5 Flash analyzes the project brief and decomposes it into structured milestones with:
     - Clear titles, scope, and concrete tangible deliverables.
     - Objective, testable acceptance criteria.
     - Cent-exact budget allocations totaling exactly $4,000.00 USD (100%).
5. Click **Submit for Bilateral Review**. The status transitions to `Pending Approval`.

---

### Step 3: Bilateral Agreement & Contract Lock
*(Both Parties Sign Off)*
1. **Bob (Freelancer, Window 2):** Clicks **Approve Plan Proposal**.
2. **Alice (Client, Window 1):** Clicks **Approve Plan Proposal**.
3. *System Action:* With dual sign-offs recorded, the Milestone Plan transitions to **AGREED**, and the project milestones become **ACTIVE**.

---

### Step 4: Freelancer Work Submission & Evidence Upload
*(As Bob Freelancer in Window 2)*
1. Click on **Milestone #1: UI/UX Architecture & Figma Tokens**.
2. Click **Submit Deliverable Work**:
   - **Description:** *"Completed high-fidelity mobile prototype with 40+ responsive screens, WCAG AAA accessibility, and design token repository."*
   - **Demo URL:** `https://github.com/example/wallet-prototype`
   - **Evidence Upload:** Drag and drop or attach a sample evidence file (e.g., sample `.txt`, `.pdf`, or `.png`).
3. Click **Submit Work for AI Evaluation**.
4. *System Action:* 
   - Files are validated (whitelist: PDF, PNG, JPG, TXT; 10 MB cap; SHA-256 hashed; stored with randomized UUID keys).
   - Work status transitions to `Submitted`.
   - Google Gemini multimodal evaluation is automatically triggered in the background.

---

### Step 5: AI Deliverable Verification & Audit Report
*(Viewable by both Client & Freelancer)*
1. On the Submission Detail view, inspect the **AI Deliverable Audit Card**:
   - **Evaluation Verdict:** `MET` (or `PARTIALLY_MET`).
   - **Confidence Score:** 92–96%.
   - **Executive Summary:** Synthesized analysis of submitted deliverables against agreed criteria.
   - **Criterion Breakdown:** Detailed status per criteria item (`Passed` / `Attention Needed`).
   - **Key Strengths & Recommended Next Steps**.

---

### Step 6: Client Deliverable Sign-off
*(As Alice Client in Window 1)*
1. Review the freelancer's evidence and the objective AI evaluation report.
2. Select **Approve Deliverable Work**:
   - Sign-off notes: *"Deliverables verified and approved. Work exceeds acceptance criteria."*
   - Click **Confirm Approval**.
3. *System Action:* Milestone #1 status transitions to **APPROVED**, unlocking payment checkout.

---

### Step 7: PayPal Sandbox Payment Checkout & Capture
*(As Alice Client in Window 1)*
1. On Milestone #1, click the **Release Payment ($2,000.00)** button.
2. The **Milestone Payment Checkout** modal displays:
   - Milestone sequence, title, and agreed canonical amount: **$2,000.00 USD**.
   - Payee details: Bob Freelancer (`bob.freelancer@judge-test.com`).
3. Choose your checkout testing mode:
   - **Mode A: Live PayPal Developer Sandbox:**
     - Select **PayPal Sandbox**.
     - Official PayPal Smart Buttons render using `@paypal/react-paypal-js`.
     - Log in with your **PayPal Sandbox Personal Buyer** credentials:
       - *Note: Do not confuse your application login with your PayPal Sandbox buyer account.*
       - Email: `buyer@personal.example.com` (or your Sandbox Buyer Account)
       - Password: (Your Sandbox Buyer Password)
     - Authorize the payment in the PayPal modal.
     - The FastAPI backend captures the transaction via PayPal REST API v2 (`/v2/checkout/orders/{id}/capture`), verifies the amount, and updates the milestone to `PAID`.
   - **Mode B: Simulated Development Mock Provider:**
     - Select **Development Mock Provider (Simulated Sandbox)**.
     - Click **Simulate Successful Payment**.
     - The backend records a simulated settlement transaction with full audit logging.
4. *Immediate Post-Payment Settlement:*
   - You are redirected to the **Payment Receipt / Confirmation Screen**.
   - Bob receives a real-time notification: `"Milestone Payment Released! Payment of USD 2,000.00 has been released by Alice Client."`
   - The Project Activity Timeline records: `"Payment Settled for 'Milestone #1' via PayPal ($2,000.00 USD)."`

---

### Step 8: Inspect Role-Based Analytics & Audits
1. Open `/dashboard` as **Alice Client**:
   - Total Projects: 1 active.
   - Committed Budget: $4,000.00.
   - Settled Payments: $2,000.00.
   - Interactive Settlement Trend Chart reflecting the captured payment.
2. Open `/dashboard` as **Bob Freelancer**:
   - Realized Earnings: $2,000.00 USD.
   - Remaining Milestone Pipeline: $2,000.00 USD.
3. Open Project Activity Timeline to see chronological, immutable audit logs with credentials and secrets redacted.

---

## 4. Security & Negative Edge Case Verification

Judges are invited to test negative edge cases to verify application security:

| Edge Case Test | Action | Expected Result |
|---|---|---|
| **Amount Tampering** | Inspect browser network tab and attempt to tamper with payment amount. | **BLOCKED:** Frontend never transmits payment amounts. Backend queries PostgreSQL and rejects any discrepancy. |
| **Unauthorized Project Access** | Attempt to view `/projects/{id}` with an unrelated user account. | **BLOCKED:** Returns HTTP 403 Forbidden / HTTP 404. |
| **Freelancer Payment Initiation** | Freelancer attempts to initiate payment checkout. | **BLOCKED:** Returns HTTP 403 Forbidden. Only assigned client can initiate checkout. |
| **Double Capture / Replay** | Re-execute capture call on an already settled payment. | **IDEMPOTENT:** Returns existing completed payment record without double billing. |
| **Malicious File Upload** | Attempt to upload `.exe`, `.sh`, or `.html` as evidence. | **BLOCKED:** Returns HTTP 400 Bad Request with whitelist rejection (PDF, PNG, JPG, TXT only). |
| **Directory Traversal** | Attempt to supply `../../etc/passwd` as filename. | **BLOCKED:** Files are assigned randomized UUID hex storage keys on disk. |
| **Bilateral Contract Lock** | Attempt to submit work on a draft milestone plan. | **BLOCKED:** Work is locked until both parties agree to the plan. |

---

## 5. Automated Test Suite Verification

Run the complete backend automated test suite:
```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```
**Result:** 79 tests passed out of 79 tests (100% pass rate).

Run the live HTTP end-to-end regression script against active servers:
```bash
cd backend
.\.venv\Scripts\python.exe scripts\verify_day8_live.py
```
**Result:** All 7 Workflows (A through G) PASSED.

