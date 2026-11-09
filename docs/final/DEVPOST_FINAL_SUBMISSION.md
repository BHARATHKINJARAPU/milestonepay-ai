# Devpost Hackathon Submission
**Project Name:** MilestonePay AI  
**Tagline:** Work Smarter. Deliver Transparently. Get Paid Confidently.  
**Track:** PayPal AI Hackathon  

---

## 1. Quick Links

- **GitHub Repository:** `https://github.com/[YOUR-USERNAME]/milestonepay-ai` *(Replace with your repository link)*
- **Hosted Application Demo:** `https://milestonepay-ai.vercel.app` *(Replace with your hosted Vercel deployment)*
- **Demo Video (YouTube):** `https://youtu.be/[YOUR-VIDEO-ID]` *(Replace with your unlisted YouTube demo video link)*

---

## 2. Short Description

**MilestonePay AI** is an AI-orchestrated freelance project and milestone payment management platform that couples **Google Gemini 2.5 Flash** with **PayPal Sandbox Checkout & Capture**. It converts ambiguous client project briefs into objective, agreed milestones, evaluates submitted deliverables automatically against agreed acceptance criteria, and authorizes instant, tamper-proof milestone payments via PayPal upon client sign-off.

---

## 3. Problem Statement

In the global freelance economy, ambiguous project scopes are the root cause of late, delayed, or withheld payments. Traditional freelance interactions suffer from three systemic friction points:

1. **Unclear Requirements & Scope Creep:** Clients frequently provide vague project descriptions. Without structured breakdown tools, freelancers make assumptions that lead to scope misalignment.
2. **Subjective Deliverable Disputes:** When work is delivered, reviewing deliverables against fuzzy expectations triggers prolonged revision cycles and interpersonal conflict.
3. **Payment Insecurity:** Freelancers risk weeks of uncompensated labor waiting for invoice approval, while clients hesitate to release payments without verifiable proof of completion.

Traditional mediation services take up to 20% commission and can take weeks to resolve disputes through human arbitration.

---

## 4. Target Audience

- **Freelance Software Engineers & Web Developers** seeking clear technical milestones and guaranteed milestone releases.
- **UI/UX & Product Designers** who need structured feedback and objective sign-off on design tokens, prototypes, and asset handoffs.
- **Independent Consultants & Content Creators** managing deliverables for non-technical clients.
- **Small Creative Agencies & Startups** requiring transparent milestone tracking and professional invoice settlement.

---

## 5. Proposed Solution

MilestonePay AI establishes an objective, high-trust bridge between clients and freelancers:

1. **AI Scope Decomposition:** Google Gemini 2.5 Flash transforms messy project descriptions into structured milestone proposals with explicit deliverables, testable acceptance criteria, and cent-exact budget splits.
2. **Bilateral Two-Party Agreement:** Neither party can unilaterally alter scope. Work is locked until both Client and Freelancer explicitly sign off.
3. **Multimodal Deliverable Audits:** When work is submitted with evidence files (PDFs, images, code repos), Gemini performs an automated, criterion-by-criterion evaluation, scoring completion confidence and highlighting gaps.
4. **Immediate PayPal Settlement:** Upon client approval, payment releases via PayPal Smart Buttons. The backend enforces monetary amounts directly from PostgreSQL to guarantee zero browser-side tampering.

---

## 6. Core Features (Completed & Verified)

- **Role-Based Authentication:** Secure Client and Freelancer accounts powered by Argon2id password hashing and signed Bearer JWT tokens.
- **Project Collaboration Engine:** Client creates projects and invites registered freelancers by email; strict non-member isolation prevents unauthorized access.
- **Gemini 2.5 Flash Milestone Generator:** Pydantic structured output converts natural-language briefs into ordered milestones with deliverables, acceptance criteria, duration estimates, and cent-exact budget allocations totaling 100%.
- **Two-Party Bilateral Agreement Lock:** Contract remains in review until both parties sign off; once agreed, milestones become active.
- **Deliverable Submission & Evidence Manager:** Supports multi-file uploads (PDF, PNG, JPG, TXT up to 10MB each) with SHA-256 cryptographic hashing and randomized UUID storage keys.
- **Multimodal AI Deliverable Audit:** Evaluates submitted evidence against agreed criteria, producing confidence scores, criterion-by-criterion status, strengths, and recommendations.
- **Client Revision & Approval Loops:** Client can request revisions with structured feedback (freezing attempt history) or authorize milestone approval.
- **PayPal Sandbox Checkout & Instant Capture:** Native integration with `@paypal/react-paypal-js` and PayPal Orders REST API v2 (`/v2/checkout/orders` and `/v2/checkout/orders/{id}/capture`).
- **Strict Backend Amount Authority:** Frontend never submits payment amounts; the backend queries PostgreSQL for canonical amounts and rejects any capture amount mismatch.
- **In-App Notifications & Activity Timeline:** Instant notifications for invitations, approvals, submissions, and payments; immutable project timeline with automatic credential sanitization.
- **Role-Aware Dashboards & Payment Analytics:** Tailored views for Clients (committed budget, settled payments, review center) and Freelancers (pipeline, realized earnings, upcoming deadlines).

---

## 7. How AI is Used

MilestonePay AI integrates **Google Gemini 2.5 Flash** (`google-genai` Python SDK) at two critical touchpoints:

1. **Pre-Project: Scope Decomposition (`gemini_service.py` & `milestone_generator.py`)**
   - The user's unstructured project brief is processed with a strict system instruction and Pydantic JSON schema (`GeminiProjectAnalysisSchema`).
   - Gemini decomposes the scope into sequential milestones, tangible deliverables, objective acceptance criteria, and budget percentage allocations.
   - A deterministic backend normalization algorithm rounds fractional percentages to ensure the sum of milestone amounts equals the total project budget to the exact cent.
2. **Post-Project: Multimodal Deliverable Audit (`deliverable_evaluator.py`)**
   - When a freelancer submits evidence (documents, architecture diagrams, demo links), Gemini audits the submission against the agreed acceptance criteria.
   - Gemini produces a structured evaluation report (`GeminiDeliverableEvaluationSchema`) containing a completion confidence score (0.0 to 1.0), individual criterion status (`met`, `partially_met`, `missed`), strengths, and areas requiring human inspection.
   - **Crucial Safety Boundary:** The AI serves strictly as an objective auditor. It never automatically approves deliverables or authorizes funds. Authoritative final sign-off remains exclusively with the authenticated client.

---

## 8. How PayPal is Integrated

MilestonePay AI integrates the **PayPal Developer Sandbox** through a robust, security-first architecture:

1. **Backend Orders Creation:**
   - When the client initiates checkout on an approved milestone, the FastAPI backend calls PayPal REST API v2 (`POST /v2/checkout/orders`) using an OAuth2 bearer token obtained with backend-only credentials.
   - The backend enforces `intent: "CAPTURE"` and passes the exact canonical milestone amount from PostgreSQL.
2. **Frontend Smart Buttons:**
   - The React frontend renders official PayPal Smart Buttons using the PayPal Web SDK v6 (`@paypal/react-paypal-js`).
   - The client authorizes the transaction in the PayPal Sandbox modal.
3. **Server-Side Capture & Validation:**
   - Upon buyer authorization, the frontend transmits the order reference to `POST /api/v1/payments/{payment_id}/capture`.
   - The backend captures the order via PayPal REST API v2 (`POST /v2/checkout/orders/{order_id}/capture`), strictly verifies that the captured amount matches the database milestone amount, records the transaction in `payments` and `payment_events`, updates the milestone to `PAID`, and triggers real-time in-app notifications.
4. **Idempotency & Fraud Defense:**
   - Duplicate capture calls are handled idempotently, returning the existing settled payment without double billing.
   - Simulated Mock Mode is strictly forbidden in production mode via Pydantic configuration validation.

---

## 9. Technical Architecture & Technology Stack

```
Frontend (React 19, TypeScript 5.8, Tailwind CSS, Vite)
       │
       │ Bearer JWT / JSON
       ▼
Backend API (FastAPI, Python 3.13, Pydantic 2, SQLAlchemy 2)
       │
       ├─► Google Gemini 2.5 Flash API (Scope Decomposition & Multimodal Audit)
       ├─► PayPal Sandbox REST API v2 (Orders & Server-side Captures)
       ├─► Local Secure File Storage (SHA-256 Hashing, UUID Storage Keys)
       └─► PostgreSQL 16 Database (Relational ACID, Alembic Migrations)
```

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript 5.8, Tailwind CSS v4, Vite 6, Lucide Icons, Axios |
| **Backend** | Python 3.13, FastAPI 0.115, SQLAlchemy 2.0, Alembic 1.14, Uvicorn |
| **Database** | PostgreSQL 16.3 with Psycopg 3 driver |
| **Authentication** | Argon2id (`argon2-cffi`), PyJWT (`pyjwt`, HS256) |
| **AI Integration** | Google Gemini 2.5 Flash (`google-genai` SDK) |
| **Payments** | PayPal REST API v2 (Sandbox), `@paypal/react-paypal-js` Web SDK v6 |
| **Testing** | Pytest 8.4, HTTPX TestClient (79 tests, 100% pass rate) |
| **Cloud Blueprints** | Render (`render.yaml`), Vercel (`frontend/vercel.json`) |

---

## 10. Implementation Challenges & Solutions

1. **Cent-Exact Budget Summation from LLM Outputs:**
   - *Challenge:* Generative LLMs frequently generate milestone percentages (e.g. 33.3%, 33.3%, 33.3%) that sum to 99.9% or exceed 100%, causing financial discrepancies.
   - *Solution:* Engineered `calculate_milestone_finances()` in Python using `Decimal` arithmetic. It normalizes percentages to 100.0 and dynamically absorbs any fractional rounding difference onto the final milestone, guaranteeing `sum(amounts) == total_budget` to the exact cent.
2. **Preventing Browser-Side Payment Amount Tampering:**
   - *Challenge:* If the client frontend passes amount parameters to the payment gateway, a malicious user could tamper with the amount in the browser network tab.
   - *Solution:* Implemented strict Backend Amount Authority. The frontend initiates checkout with only a milestone ID. The backend queries PostgreSQL for the canonical amount, transmits it to PayPal, and validates the returned capture payload.
3. **Preserving Audit Trails across Deliverable Revisions:**
   - *Challenge:* If a client requests revisions on a submission, modifying the original submission in-place would overwrite historical feedback and AI audits.
   - *Solution:* Implemented an attempt-versioning model (`attempt_number`). When revisions are requested, Attempt #1 is locked in `revision_requested` status with its client review comments, and the freelancer creates Attempt #2, preserving complete historical review integrity.

---

## 11. Real-World Impact

MilestonePay AI introduces transparency, objective quality verification, and payment certainty to the freelance economy:
- Eliminates scope creep disputes by enforcing mutual agreement on acceptance criteria before work begins.
- Accelerates invoice approval from weeks to seconds by providing objective AI deliverable audits.
- Guarantees immediate milestone funds settlement through PayPal's trusted global infrastructure.

---

## 12. Future Scope (Planned Enhancements)

- **PayPal Multi-Seller Marketplace Split Payouts:** Integrate PayPal Marketplace / Commerce Platform to automate split payouts between freelancers and platform commissions.
- **Client Pre-Funded Escrow:** Enable clients to pre-fund entire milestone plans upon contract agreement.
- **Native Git PR Integration:** GitHub and GitLab webhooks that automatically submit deliverables when pull requests are merged.
- **Multi-Currency Dynamic Conversion:** Real-time cross-currency conversions using PayPal FX APIs.

