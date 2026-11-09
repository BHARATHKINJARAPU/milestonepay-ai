# MilestonePay AI — Render Web Service Backend Setup Guide

This guide details setting up the FastAPI backend on a **paid Render Web Service**.

---

## 1. Web Service Specifications

- **Target Service Name:** `milestonepay-api`
- **Region:** `Oregon (US West)` *(must match database region)*
- **Root Directory:** `backend`
- **Runtime:** `Python 3`
- **Instance Type:** `Starter` ($7/mo) or `Standard` ($25/mo)
  - Paid tiers stay awake 24/7 without cold starts or spin-downs.
  - Supports persistent disk attachments and outbound static IP (if needed).
- **Application Entry Point:** [`backend/app/main.py`](../../backend/app/main.py) (`app.main:app`)

---

## 2. Service Creation Steps (Render Dashboard)

1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Web Service**.
3. Choose **Build and deploy from a Git repository** and connect:
   `https://github.com/BHARATHKINJARAPU/milestonepay-ai`
4. In the configuration form, specify:
   - **Name:** `milestonepay-api`
   - **Region:** `Oregon (US West)`
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
     ```
   - **Start Command:**
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** Select **Starter** or **Standard** (paid tier).

---

## 3. Persistent Disk for Evidence Storage (Optional but Recommended)

Render Web Services have ephemeral filesystems by default. To preserve uploaded evidence files across service restarts and redeployments:
1. In the Web Service configuration (or under **Disks** in settings), click **Add Disk**.
2. **Name:** `milestonepay-uploads`
3. **Mount Path:** `/var/data/uploads`
4. **Size:** `10 GB` (Starter disk is $2.50/mo for 10 GB).
5. In your Environment Variables, set:
   ```
   UPLOAD_DIR=/var/data/uploads
   ```

---

## 4. Health Check Path & Auto-Recovery

In the **Advanced** section of service settings:
- **Health Check Path:** `/api/v1/health`
- Render periodically polls this endpoint via HTTP GET. If Uvicorn fails to respond, Render automatically terminates the instance and spins up a healthy container.
- For deep readiness checks (database connectivity verification), the application also provides `/api/v1/health/ready`.

---

## 5. Production Environment Variables

Navigate to the **Environment** tab of your Render Web Service and add the following variables:

| Variable | Value / Format | Purpose |
| :--- | :--- | :--- |
| `APP_NAME` | `MilestonePay AI` | Application banner and logging tag |
| `ENVIRONMENT` | `production` | Enables strict security guards (disables mock payments) |
| `API_V1_PREFIX` | `/api/v1` | Base route prefix |
| `DATABASE_URL` | `<Internal Database URL from milestonepay-db>` | Direct connection to Render PostgreSQL |
| `CORS_ORIGINS` | `https://<YOUR-VERCEL-DOMAIN>.vercel.app` | Whitelist for Vercel frontend requests |
| `JWT_SECRET_KEY` | *(Generate 64-char random string via `openssl rand -hex 32`)* | Signs HMAC-SHA256 session tokens |
| `JWT_ALGORITHM` | `HS256` | Token signature algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | Session lifetime (2 hours) |
| `GEMINI_API_KEY` | *(Your Google Gemini API Key from Google AI Studio)* | AI milestone generation and deliverable audit |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model variant |
| `PAYMENT_PROVIDER` | `paypal` | Primary payment engine |
| `PAYPAL_MODE` | `sandbox` | Active sandbox mode |
| `PAYPAL_API_BASE_URL` | `https://api-m.sandbox.paypal.com` | Official PayPal Sandbox API endpoint |
| `PAYPAL_CLIENT_ID` | *(Your PayPal Sandbox REST Client ID)* | Backend OAuth authentication |
| `PAYPAL_CLIENT_SECRET` | *(Your PayPal Sandbox REST Client Secret)* | Backend OAuth authentication |
| `PAYPAL_WEBHOOK_ID` | *(Optional, set after creating webhook in PayPal)* | Inbound webhook signature verification |
| `PAYPAL_CURRENCY` | `USD` | Standard transaction currency |
| `PAYPAL_REQUEST_TIMEOUT_SECONDS`| `20.0` | Network timeout for PayPal REST calls |
| `UPLOAD_DIR` | `/var/data/uploads` *(if disk attached, else `./uploads`)* | Evidence storage location |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum file size limit |
| `MAX_EVIDENCE_FILES` | `5` | Maximum upload count per submission |

---

## 6. Service Verification

Once Render finishes building and starts the container:
1. Copy your public service URL (e.g., `https://milestonepay-api.onrender.com`).
2. Verify basic liveness in your browser or terminal:
   ```bash
   curl -i https://milestonepay-api.onrender.com/api/v1/health
   # HTTP/1.1 200 OK
   # {"status":"healthy","service":"milestonepay-api"}
   ```
3. Verify database readiness:
   ```bash
   curl -i https://milestonepay-api.onrender.com/api/v1/health/ready
   # HTTP/1.1 200 OK
   # {"status":"ready","service":"milestonepay-api","database":"connected"}
   ```
