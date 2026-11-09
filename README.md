# MilestonePay AI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.13](https://img.shields.io/badge/Python-3.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI: 0.115](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React: 19](https://img.shields.io/badge/React-19.0-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript: 5.8](https://img.shields.io/badge/TypeScript-5.8-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL: 16](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Google Gemini: 2.5](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-8E75C2.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![PayPal: REST v2](https://img.shields.io/badge/PayPal-REST%20v2%20Sandbox-00457C.svg?logo=paypal&logoColor=white)](https://developer.paypal.com/)
[![Tests: 83 Passed](https://img.shields.io/badge/Tests-83%20Passed%20(100%25)-success.svg)](backend/tests/)

> **Work Smarter. Deliver Transparently. Get Paid Confidently.**

MilestonePay AI is an AI-powered freelance milestone and payment orchestration platform created for the **PayPal AI Hackathon**.

Freelancers and clients lose billions every year to ambiguous project scopes, subjective revisions, and delayed milestone payments. MilestonePay AI turns unstructured project descriptions into objective, agreed milestones using **Google Gemini 2.5 Flash**, verifies submitted evidence artifacts with multimodal AI audits, and authorizes instant, tamper-proof payment releases via **PayPal Sandbox Checkout**.

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Client (React 19 + TypeScript + Tailwind)"]
        UI["SPA Interface (Vite)"]
        AUTH_CTX["Auth Context & Token Interceptor"]
        PAYPAL_SDK["PayPal Web SDK v6 (@paypal/react-paypal-js)"]
    end

    subgraph APILayer["FastAPI Application Backend (Python 3.13)"]
        ROUTER["REST API Router (/api/v1)"]
        AUTH_SVC["Auth Service (Argon2id + PyJWT)"]
        PROJECT_SVC["Project & Member Service"]
        PLAN_SVC["Milestone Plan & Contract Lock Service"]
        SUB_SVC["Deliverable Submission & Evidence Manager"]
        PAY_SVC["Payment & PayPal Orchestration Service"]
        NOTIF_SVC["In-App Notification & Activity Service"]
        ANALYTICS_SVC["Role-Based Analytics & Trends Engine"]
    end

    subgraph ExternalServices["External APIs & AI Services"]
        GEMINI["Google Gemini 2.5 Flash API"]
        PAYPAL_API["PayPal Sandbox REST API v2"]
    end

    subgraph DataLayer["Persistence & Storage"]
        PG["PostgreSQL 16 Database"]
        STORAGE["Encrypted Evidence File Storage (SHA-256)"]
    end

    UI --> AUTH_CTX
    AUTH_CTX -->|Bearer JWT| ROUTER
    PAYPAL_SDK -->|Order Token| PAYPAL_API

    ROUTER --> AUTH_SVC
    ROUTER --> PROJECT_SVC
    ROUTER --> PLAN_SVC
    ROUTER --> SUB_SVC
    ROUTER --> PAY_SVC
    ROUTER --> NOTIF_SVC
    ROUTER --> ANALYTICS_SVC

    PLAN_SVC -->|Decompose Scope| GEMINI
    SUB_SVC -->|Multimodal Audit| GEMINI
    PAY_SVC -->|Create & Capture Orders| PAYPAL_API

    AUTH_SVC --> PG
    PROJECT_SVC --> PG
    PLAN_SVC --> PG
    SUB_SVC --> PG
    SUB_SVC --> STORAGE
    PAY_SVC --> PG
    NOTIF_SVC --> PG
    ANALYTICS_SVC --> PG
```

---

## 2. End-to-End Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Client
    actor Freelancer
    participant App as MilestonePay Frontend
    participant API as FastAPI Backend
    participant Gemini as Google Gemini 2.5 Flash
    participant PayPal as PayPal Sandbox API

    Client->>App: Creates project with unstructured brief ($5,000 budget)
    Client->>App: Invites Freelancer via email
    App->>API: POST /projects/{id}/members
    API-->>Freelancer: In-App Notification (Collaborator Added)

    Freelancer->>App: Requests AI Milestone Breakdown
    App->>API: POST /projects/{id}/milestone-plans/generate
    API->>Gemini: Prompts Gemini 2.5 Flash with Pydantic Schema
    Gemini-->>API: 2-Milestone Breakdown (summing to exactly $5,000.00)
    API-->>App: Milestone Plan (Draft)

    Client->>App: Signs and approves plan
    Freelancer->>App: Signs and approves plan
    App->>API: POST /projects/{id}/milestone-plans/{id}/approve (x2)
    API-->>App: Plan transitions to AGREED; Milestones become ACTIVE

    Freelancer->>App: Submits Milestone 1 with evidence artifacts (PDF, PNG, Demo URL)
    App->>API: POST /projects/{id}/milestones/{id}/submissions + POST evidence
    App->>API: POST /submissions/{id}/submit
    API->>Gemini: Multimodal Deliverable Audit vs Agreed Criteria
    Gemini-->>API: Evaluation Report (Score: 95%, Met: Yes, Criterion Findings)
    API-->>App: Submission in SUBMITTED state with AI Audit Report

    Client->>App: Reviews AI Audit Report and approves deliverable
    App->>API: POST /submissions/{id}/approve
    API-->>App: Milestone status transitions to APPROVED; Unlocks Payment

    Client->>App: Clicks 'Release Payment ($2,000.00)'
    App->>API: POST /projects/{id}/milestones/{id}/payments
    API->>PayPal: POST /v2/checkout/orders (Amount enforced from PostgreSQL)
    PayPal-->>App: PayPal Smart Buttons Checkout Modal
    Client->>PayPal: Authorizes payment in PayPal Sandbox
    PayPal-->>App: onApprove(orderId)
    App->>API: POST /payments/{id}/capture
    API->>PayPal: POST /v2/checkout/orders/{id}/capture
    PayPal-->>API: Status COMPLETED ($2,000.00)
    API->>API: Verifies capture amount == database milestone amount
    API->>API: Marks Milestone PAID & creates immutable Activity log
    API-->>Freelancer: Instant In-App Notification (Payment Released)
    API-->>App: Payment Receipt & Settled State
```

---

## 3. Technology Stack

| Domain | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend** | React | 19.0.0 | Component hierarchy, state management, modern hooks |
| **Frontend Language** | TypeScript | 5.8.2 | Strict type safety and end-to-end interface parity |
| **Styling** | Tailwind CSS | 4.0.0 | High-performance CSS design system |
| **Icons** | Lucide React | 1.16.0 | Professional accessible iconography |
| **Payments SDK** | `@paypal/react-paypal-js` | 8.8.2 | Official PayPal Web SDK v6 Smart Buttons |
| **HTTP Client** | Axios | 1.7.9 | Request/response interceptors with Bearer token injection |
| **Backend** | FastAPI | 0.115.11 | High-throughput asynchronous REST API framework |
| **Backend Language** | Python | 3.13 | Core runtime |
| **Database** | PostgreSQL | 16.3 | Relational ACID database with JSONB support |
| **ORM** | SQLAlchemy | 2.0.38 | Parameterized queries with relationship loading |
| **Migrations** | Alembic | 1.14.1 | Schema revision versioning |
| **Password Security** | Argon2id (`argon2-cffi`) | 23.1.0 | OWASP-recommended memory-hard hashing |
| **Token Security** | PyJWT | 2.10.1 | Signed HMAC-SHA256 access tokens |
| **AI Engine** | Google Gemini | 2.5 Flash | Generative scope decomposition and multimodal evaluation |
| **Payment Gateway** | PayPal REST API v2 | Sandbox | Orders, Captures, Webhooks, Idempotent Processing |
| **Testing** | Pytest + HTTPX | 8.4.2 | 79 automated tests (100% pass rate) |

---

## 4. Key Highlights & Capabilities

1. **Google Gemini 2.5 Flash Scope Decomposition:**
   - Prompts Gemini with rigid Pydantic schemas.
   - Decomposes ambiguous requirements into ordered milestones with explicit deliverables, testable acceptance criteria, and cent-exact financial splits.
2. **Two-Party Bilateral Agreement Workflow:**
   - Milestone plan is locked in `draft` or `pending_approval` until **both** client and freelancer explicitly sign off.
   - Prevents unilateral scope creep.
3. **Multimodal Deliverable Evidence Management:**
   - Whitelist validation (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`).
   - 10 MB per-file size enforcement.
   - SHA-256 cryptographic hashing and randomized UUID storage keys (directory traversal immune).
4. **AI Deliverable Audit & Scoring:**
   - Gemini compares submitted files and demo links against agreed acceptance criteria.
   - Outputs completion score, criterion status (`met`, `partially_met`, `missed`), strengths, and actionable feedback.
5. **PayPal Sandbox Checkout & Instant Capture:**
   - Official PayPal Smart Buttons rendered client-side.
   - Backend creates order using official PayPal Orders REST API v2.
   - Instant capture updates database state and releases funds.
6. **Strict Backend Amount Authority:**
   - Browser never transmits amount fields.
   - Backend queries PostgreSQL for canonical milestone amount and validates capture responses.
7. **Dual Mode Payment Processing:**
   - **PayPal Mode:** Full PayPal Sandbox checkout with live order capture.
   - **Mock Mode:** Built-in simulated provider for development environments without requiring active PayPal credentials.
8. **Real-Time In-App Notifications & Activity Audits:**
   - Instant unread badge alerts for invitations, approvals, submissions, and payments.
   - Immutable project activity timeline with automatic credential/token redaction.

---

## 5. Quickstart & Local Setup

### Prerequisites
- **Python 3.12+** (tested on 3.13)
- **Node.js 20+** and `npm`
- **PostgreSQL 16**

---

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/milestonepay-ai.git
cd milestonepay-ai
```

---

### Step 2: Configure Environment Variables

**Backend (`backend/.env`):**
```bash
cp backend/.env.example backend/.env
```
Key configuration values in `backend/.env`:
```ini
APP_NAME=MilestonePay AI
ENVIRONMENT=development
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://milestonepay:milestonepay_dev_password@localhost:5432/milestonepay_dev
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
JWT_SECRET_KEY=milestonepay_dev_jwt_secret_key_849302194820194820194820
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Payment Configuration
PAYMENT_PROVIDER=mock          # Change to 'paypal' for real PayPal Sandbox checkout
PAYPAL_MODE=sandbox
PAYPAL_API_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_paypal_sandbox_client_secret
PAYPAL_CURRENCY=USD
```

**Frontend (`frontend/.env`):**
```bash
cp frontend/.env.example frontend/.env
```
```ini
VITE_API_BASE_URL=http://localhost:8000
VITE_PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id
```

---

### Step 3: Start Backend & Run Migrations
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate   # Windows (source .venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/v1/health/ready`

---

### Step 4: Start Frontend
```bash
cd frontend
npm install
npm run dev
```
- Frontend Application: `http://localhost:5173`

---

## 6. Automated Testing

MilestonePay AI comes with 100% automated test coverage across all subsystems:

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

**Output:**
```
======================= 83 passed, 1 warning in 54.50s =======================
```

To run frontend TypeScript validation and production bundling checks:
```bash
cd frontend
npm run build
```

---

## 7. Production Deployment & Cloud Guides

MilestonePay AI includes ready-to-deploy specifications and detailed production deployment manuals:

- **Backend (Render):** Defined in [`render.yaml`](render.yaml). Deploys FastAPI web service alongside managed PostgreSQL. Includes automatic Alembic migration on deploy. Full guide: [Render Deployment Guide](docs/release/RENDER_DEPLOYMENT_GUIDE.md).
- **Frontend (Vercel):** Defined in [`frontend/vercel.json`](frontend/vercel.json). Configured with single-page application rewrites and production security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`). Full guide: [Vercel Deployment Guide](docs/release/VERCEL_DEPLOYMENT_GUIDE.md).
- **End-to-End Production Guide:** [Full Deployment Guide](docs/release/DEPLOYMENT_GUIDE.md).
- **GitHub Push Guide:** [GitHub Repository Connection Guide](docs/release/GITHUB_PUSH_GUIDE.md).

---

## 8. Release Verification & Hackathon Resources

- **[Release Gates Checklist](docs/release/RELEASE_CHECKLIST.md):** 12-point release gate audit (all passed).
- **[Final Test Execution Report](docs/release/FINAL_TEST_REPORT.md):** Detailed breakdown of all 83 backend tests.
- **[Security & Secret Audit](docs/release/SECURITY_REPORT.md):** OWASP & PCI DSS audit verifying zero secret leakage.
- **[Repository Architecture Audit](docs/release/REPOSITORY_AUDIT.md):** Comprehensive component audit & bug fix log.
- **[Judge Testing & Evaluation Guide](docs/JUDGE_TESTING_GUIDE.md):** Step-by-step walkthrough for evaluating the platform.
- **[Demo Video Script & Checklist](docs/DEMO_VIDEO_SCRIPT.md):** 2m 45s timed video recording script.
- **[Devpost Submission Packet](docs/DEVPOST_SUBMISSION.md):** Complete hackathon submission copy.
- **[Open Source License](LICENSE):** MIT License.

---

## 9. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
