# MilestonePay AI — Security & Secret Audit Report

**Audit Date:** November 9, 2026  
**Security Standard:** OWASP Top 10 • PCI DSS Merchant Guidance • Fintech Defense-in-Depth  
**Secret Scan Status:** PASS (0 secrets detected in working tree or Git commit history)  

---

## 1. Secret Scanning Results

A custom regex scanner (`backend/scripts/secret_scan.py`) executed against all files in the repository and the full Git commit log (`git log -p`).

### Scanner Configuration & Signatures
1. **Google Gemini / Cloud API Key:** `AIza[0-9A-Za-z\-_]{35}`
2. **PayPal Access Token / App Secret:** `EA[0-9A-Za-z\-_]{50,}`
3. **PayPal Client Secret Candidate:** `(?:paypal_client_secret|client_secret)\s*[:=]\s*['"]([A-Za-z0-9_-]{30,})['"]`
4. **Gemini Key Candidate:** `(?:gemini_api_key)\s*[:=]\s*['"]([A-Za-z0-9_-]{20,})['"]`
5. **PostgreSQL URI Passwords:** `postgres(?:ql)?:\/\/[a-zA-Z0-9_-]+:([a-zA-Z0-9_%#@!]+)@`

### Findings
- **Workspace Files:** 0 secrets found.
- **Git Commit History:** 0 secrets found.
- **Result:** **100% CLEAN**. No credentials have ever been committed into Git.

---

## 2. Git Ignore Verification

Both root and subdirectory `.gitignore` files were inspected:
- **Root `.gitignore`**:
  ```gitignore
  # Environment configuration
  .env
  .env.*
  !.env.example
  !.env.*.example
  ```
- **Backend `.gitignore`**:
  Explicitly ignores `.venv/`, `.env`, `.env.*`, `uploads/`, `*.log`, `__pycache__/`, `.pytest_cache/`.
- **Frontend `.gitignore`**:
  Explicitly ignores `node_modules/`, `dist/`, `.env`, `.env.*`, `!.env.example`.

All real local `.env` files (`backend/.env`, `frontend/.env`, `frontend/.env.development`) are unversioned and strictly ignored by Git.

---

## 3. Financial & Access Security Controls

### 3.1 Backend Amount Authority
- Neither frontend client code nor the browser can supply or override transaction amounts.
- When `POST /api/v1/projects/{id}/milestones/{id}/payments` is called, the backend queries the database for the agreed milestone row and constructs the PayPal order payload using the exact PostgreSQL decimal value.
- When `POST /api/v1/payments/{id}/capture` is called, the backend queries PayPal's live order before capture and ensures `purchase_units[0].amount.value` and `currency_code` match the database authority.

### 3.2 PayPal OAuth Credential Isolation
- `PAYPAL_CLIENT_SECRET` is maintained strictly inside the backend environment.
- Only the public `PAYPAL_CLIENT_ID` is exposed to the frontend browser if required for client-side SDK rendering.
- All access tokens obtained from `https://api-m.sandbox.paypal.com/v1/oauth2/token` are cached in server memory and never returned in API responses.

### 3.3 JWT Authentication & Session Security
- User passwords are encrypted with BCrypt (`passlib[bcrypt]`, 12 work rounds).
- JWTs are signed with HS256 using `JWT_SECRET_KEY` and include subject ID, expiration time, and role.
- Endpoints enforce authorization headers: `Authorization: Bearer <token>`.
- Token extraction and user validation occur on every protected endpoint via `get_current_active_user`.

### 3.4 Evidence File Upload Security
- Files uploaded as deliverable evidence are inspected for size (max 10MB) and allowed MIME types (PDF, PNG, JPG, ZIP, TXT, MD, DOCX).
- Files are saved to disk using cryptographically secure UUID storage keys rather than user-supplied filenames to prevent path traversal (`../../`) attacks.
- Download endpoint requires authentication and verifies that the requesting user is an active member of the project workspace.

### 3.5 Webhook Signature Verification
- Inbound PayPal webhooks are received at `/api/v1/webhooks/paypal`.
- Webhook signature headers (`paypal-auth-algo`, `paypal-cert-url`, `paypal-transmission-id`, `paypal-transmission-sig`, `paypal-transmission-time`) are validated against PayPal's verification API.
- Processed events are recorded in `paypal_webhook_events` with unique event IDs to guarantee idempotent deduplication.

---

## 4. Production Security Recommendations

1. **Secret Rotation:** When moving from Sandbox to Production, generate fresh PayPal Live credentials and Gemini API keys.
2. **CORS Whitelist:** Set `CORS_ORIGINS` to the exact deployed frontend URL (e.g., `https://milestonepay-ai.vercel.app`) without trailing slashes. Never use `*` with credentialed requests.
3. **HTTPS Everywhere:** Both Vercel (frontend) and Render (backend) enforce TLS 1.3 by default. Ensure secure cookies and HSTS headers are enabled.
4. **Database Encryption:** Render managed PostgreSQL encrypts data at rest and requires SSL (`sslmode=require`) for all external connections.
