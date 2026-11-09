# MilestonePay AI — Production Deployment Guide

**Target Architecture:**
- **Frontend:** Vercel Edge Network (React 18 + TypeScript + Vite SPA)
- **Backend:** Render Managed Web Service (FastAPI + Python 3.13 + Uvicorn)
- **Database:** Render Managed PostgreSQL 16 (High Availability / Automated Backups)
- **AI Engine:** Google Gemini 2.5 Flash API
- **Payments:** PayPal Sandbox REST API v2 & Webhooks

---

## 1. Environment Variables Inventory

### 1.1 Backend Environment (Render Dashboard)
| Variable Name | Required | Example / Description |
| :--- | :--- | :--- |
| `APP_NAME` | Yes | `MilestonePay AI` |
| `ENVIRONMENT` | Yes | `production` |
| `API_V1_PREFIX` | Yes | `/api/v1` |
| `DATABASE_URL` | Yes | Internal connection string from Render PostgreSQL (e.g., `postgresql+psycopg://user:pass@dpg-xxx:5432/milestonepay`) |
| `CORS_ORIGINS` | Yes | Deployed frontend domain: `https://milestonepay-ai.vercel.app` (comma-separated for multiples) |
| `JWT_SECRET_KEY` | Yes | 64-character cryptographically random hex string |
| `JWT_ALGORITHM` | Yes | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | `120` |
| `GEMINI_API_KEY` | Yes | Google Gemini API key obtained from Google AI Studio |
| `GEMINI_MODEL` | Yes | `gemini-2.5-flash` |
| `PAYMENT_PROVIDER` | Yes | `paypal` |
| `PAYPAL_MODE` | Yes | `sandbox` (or `live` in production) |
| `PAYPAL_API_BASE_URL` | Yes | `https://api-m.sandbox.paypal.com` |
| `PAYPAL_CLIENT_ID` | Yes | Sandbox REST Application Client ID |
| `PAYPAL_CLIENT_SECRET` | Yes | Sandbox REST Application Secret |
| `PAYPAL_WEBHOOK_ID` | No | Registered Webhook ID from PayPal Developer Portal |
| `PAYPAL_CURRENCY` | Yes | `USD` |
| `MAX_UPLOAD_SIZE_MB` | No | `10` |
| `MAX_EVIDENCE_FILES` | No | `5` |

### 1.2 Frontend Environment (Vercel Dashboard)
| Variable Name | Required | Example / Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Yes | Full HTTPS URL of deployed Render backend: `https://milestonepay-api.onrender.com` |
| `VITE_PAYPAL_CLIENT_ID` | Yes | Public PayPal Sandbox Client ID (identical to backend `PAYPAL_CLIENT_ID`) |

> [!CAUTION]
> Never set `GEMINI_API_KEY`, `PAYPAL_CLIENT_SECRET`, `JWT_SECRET_KEY`, or `DATABASE_URL` in Vercel. Frontend bundles are publicly readable.

---

## 2. Backend Deployment on Render

### Step 1: Create Render PostgreSQL Database
1. Go to the [Render Dashboard](https://dashboard.render.com/) and click **New > PostgreSQL**.
2. **Name:** `milestonepay-db`
3. **Database:** `milestonepay`
4. **User:** `milestonepay_user`
5. **Region:** Choose `Oregon (US West)` (or closest to your target users).
6. **Plan:** Choose `Starter` or `Standard` for persistent data and daily backups. (Note: Render Free Postgres expires after 30 days and has no backups).
7. Once provisioned, copy the **Internal Database URL** (for backend services in the same region).

### Step 2: Create Render Web Service
1. Click **New > Web Service** and select your GitHub repository: `milestonepay-ai`.
2. **Name:** `milestonepay-api`
3. **Region:** Must match your database region (`Oregon (US West)`).
4. **Root Directory:** `backend`
5. **Runtime:** `Python 3`
6. **Build Command:**
   ```bash
   pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
   ```
7. **Start Command:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
8. **Health Check Path:** `/api/v1/health`

### Step 3: Configure Environment Variables
In the service's **Environment** tab, add all variables from the Backend table above.  
For `DATABASE_URL`, paste the Internal Database URL from Step 1, changing the scheme prefix to `postgresql+psycopg://` if needed.

### Step 4: Verify Deployment
Once build completes, verify via terminal:
```bash
curl -s https://milestonepay-api.onrender.com/api/v1/health/ready
# Expected: {"status":"ready","service":"milestonepay-api","database":"connected"}
```

---

## 3. Frontend Deployment on Vercel

### Step 1: Import Project into Vercel
1. Go to [Vercel Dashboard](https://vercel.com/) and click **Add New > Project**.
2. Import your GitHub repository: `milestonepay-ai`.
3. In project settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click `Edit` and select `frontend`.
   - **Build Command:** `npm run build` (or default `tsc -b && vite build`)
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`

### Step 2: Configure Environment Variables
Add the two frontend environment variables:
- `VITE_API_BASE_URL`: `https://milestonepay-api.onrender.com`
- `VITE_PAYPAL_CLIENT_ID`: Your PayPal Sandbox Client ID

### Step 3: Deploy & Verify
Click **Deploy**. Once finished:
1. Open the Vercel deployment URL in your browser.
2. Verify registration and login connect to the Render backend.
3. Update `CORS_ORIGINS` in your Render Web Service to include this exact Vercel URL.

---

## 4. Evidence Storage in Production

- In development, evidence files are stored in `backend/uploads/`.
- Render web service containers have **ephemeral filesystems** by default (files reset on redeploy or restart).
- For production deployments requiring permanent evidence file retention:
  1. Attach a **Render Persistent Disk** mounted at `/app/backend/uploads`, OR
  2. Configure an AWS S3 / Cloudflare R2 bucket with private ACLs and authenticated pre-signed URLs.

---

## 5. PayPal Webhook Registration

To receive real-time payment capture callbacks:
1. Log into the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/).
2. Select your Sandbox REST application.
3. Scroll to **Webhooks** and click **Add Webhook**.
4. **Webhook URL:** `https://milestonepay-api.onrender.com/api/v1/webhooks/paypal`
5. **Event Types:** Select:
   - `PAYMENT.CAPTURE.COMPLETED`
   - `PAYMENT.CAPTURE.DENIED`
   - `CHECKOUT.ORDER.APPROVED`
6. Copy the generated **Webhook ID** and save it in Render backend environment as `PAYPAL_WEBHOOK_ID`.
