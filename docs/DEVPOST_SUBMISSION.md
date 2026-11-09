# Devpost Hackathon Submission Packet
**Project Name:** MilestonePay AI  
**Tagline:** Work Smarter. Deliver Transparently. Get Paid Confidently.  
**Track:** PayPal AI Hackathon  

---

## 1. Project Overview

### The Problem
The global freelance economy exceeds \$1.5 trillion, yet over **70% of freelancers report experiencing late, delayed, or withheld payments**, and **58% of clients complain of scope misalignment and unclear deliverables**. 

Traditional freelance platforms rely on subjective human mediation, high dispute fees (up to 20%), and prolonged review cycles. Clients are hesitant to release funds when deliverable quality is ambiguous, while freelancers risk non-payment after investing weeks of uncompensated labor.

### The Solution: MilestonePay AI
**MilestonePay AI** is an intelligent, AI-orchestrated freelance project and milestone payment management platform. By coupling **Google Gemini 2.5 Flash** with **PayPal Developer Sandbox (REST API v2 + Web SDK v6)**, MilestonePay AI establishes an objective, high-trust payment bridge:

1. **Unstructured Briefs to Structured Milestones:** Gemini converts ambiguous project descriptions into structured milestones with concrete deliverables, objective acceptance criteria, duration estimates, and cent-exact budget allocations totaling 100%.
2. **Bilateral Contract Lock:** Scope cannot be changed unilaterally. Work is locked until both Client and Freelancer review and sign off.
3. **Multimodal Deliverable Evaluation:** When freelancers submit work with evidence files (PDFs, images, code repos), Gemini performs an automated, criterion-by-criterion audit, scoring completion confidence and pinpointing any remaining gaps.
4. **Instant PayPal Settlement:** Upon client deliverable approval, payment checkout unlocks with official PayPal Smart Buttons. The FastAPI backend verifies amount authority directly against PostgreSQL records, captures orders via PayPal REST API v2, and marks milestones paid in real-time.

---

## 2. Key Features

- **Google Gemini 2.5 Scope Decomposition:** Structured outputs convert vague briefs into ordered milestones, deliverables, criteria, and cent-accurate financial splits.
- **Two-Party Bilateral Agreement Workflow:** Ensures both client and freelancer explicitly sign off on proposed milestones before any work commences.
- **Multimodal Deliverable Evidence Management:** Secure evidence file upload system with size throttling (10 MB), extension whitelisting (PDF, PNG, JPG, TXT), SHA-256 cryptographic hashing, and randomized UUID keys.
- **AI Deliverable Audit & Confidence Scoring:** Gemini assesses submitted evidence against agreed acceptance criteria, providing transparent findings to both parties.
- **PayPal Sandbox Checkout & Instant Capture:** Native integration with `@paypal/react-paypal-js` and PayPal Orders REST API v2.
- **Strict Backend Amount Authority:** Zero trust in client-side monetary inputs; backend queries PostgreSQL amounts and rejects tampering or duplicate capture attempts.
- **Development Mock Provider Mode:** Full simulated payment flow for local environments without requiring active PayPal credentials.
- **Role-Aware Dashboards & Settlement Trends:** Dedicated client vs freelancer views with real-time in-app notifications and immutable project activity audit logs.

---

## 3. How We Built It

### Architecture
- **AI Core:** Google Gemini 2.5 Flash (`google-genai` SDK) utilizing Pydantic structured schemas for deterministic JSON parsing.
- **Payment Gateway:** PayPal Sandbox REST API v2 (`/v2/checkout/orders` & `/v2/checkout/orders/{id}/capture`), PayPal Webhooks, and PayPal Web SDK v6.
- **Backend API:** Python 3.13, FastAPI, SQLAlchemy 2.0 ORM, PostgreSQL 16, Alembic migrations, Argon2id password hashing, PyJWT authentication.
- **Frontend SPA:** React 19, TypeScript 5.8, Tailwind CSS, Vite, Lucide Icons, Axios request/response interceptors.
- **Deployment Ready:** Render blueprint (`render.yaml`) for backend + managed PostgreSQL; Vercel (`vercel.json`) for frontend SPA.

---

## 4. Challenges We Overcame

1. **Deterministic Financial Summation in AI Outputs:** LLMs occasionally hallucinate fractional percentages that do not sum to 100%. We engineered a robust normalization and rounding algorithm that guarantees the sum of milestone amounts equals the total project budget to the exact cent.
2. **Eliminating Payment Amount Tampering:** Ensuring the client cannot modify checkout amounts in the browser. We implemented strict backend amount authority: the frontend initiates checkout referencing only milestone IDs; the backend looks up the canonical database amount, passes it directly to PayPal's API, and validates the returned capture payload.
3. **Multimodal Evidence Handling:** Accommodating multiple evidence file types while maintaining strict sandbox isolation and fast response times. We built chunked streaming file storage with SHA-256 integrity validation and structured Gemini prompting.
4. **Idempotency in Payment Processing:** Preventing accidental double billing if network hiccups cause duplicate capture requests. All capture endpoints and webhooks implement atomic status checks and idempotency keys.

---

## 5. Accomplishments That We're Proud Of

- **100% Automated Backend Test Coverage:** 79 comprehensive tests passing with `pytest` across auth, projects, Gemini generation, bilateral approval, deliverable uploads, AI audits, and PayPal order captures.
- **Zero Frontend Errors:** Production build compiles cleanly with zero TypeScript or linter errors.
- **Dual Payment Flexibility:** Seamlessly toggles between real PayPal Sandbox and a simulated mock provider with strict production safeguards.
- **End-to-End Live Integration:** Verified with an automated live HTTP integration script testing all 14 lifecycle stages against a live database.

---

## 6. What We Learned

- How to combine generative AI reasoning with deterministic financial systems: AI should assist and audit, but deterministic code and database constraints must enforce contract terms and payment amounts.
- PayPal REST API v2 best practices for server-side order capture, idempotent event processing, and SDK integration.

---

## 7. What's Next for MilestonePay AI

- **PayPal Multi-Seller Marketplace Split Payouts:** Automating platform commissions and instant payouts to freelancer PayPal wallets.
- **Automated Escrow Pre-Funding:** Enabling clients to pre-fund entire milestone plans into escrow upon initial plan agreement.
- **Git Provider Webhooks:** Native GitHub/GitLab PR integration for automated evidence submission directly from pull requests.
- **Cross-Currency FX Support:** Real-time multi-currency conversions using PayPal currency conversion APIs.

