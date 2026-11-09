# MilestonePay AI — Render Backend & Database Deployment Guide

This guide details deploying the FastAPI backend and managed PostgreSQL database on Render.

---

## Deployment Option A: Automatic Blueprint Deployment (`render.yaml`)

The repository includes a production-ready `render.yaml` blueprint at the root:

1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New > Blueprint**.
3. Connect your GitHub repository: `milestonepay-ai`.
4. Render will parse `render.yaml` and propose creating:
   - **PostgreSQL Database:** `milestonepay-db` (Oregon region, standard plan).
   - **Web Service:** `milestonepay-api` (Oregon region, Python 3, root dir `backend`).
5. Render will automatically generate `JWT_SECRET_KEY` and link the internal database URL.
6. Provide the non-synced environment variables when prompted:
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `PAYPAL_CLIENT_ID`: Your PayPal Sandbox REST Client ID.
   - `PAYPAL_CLIENT_SECRET`: Your PayPal Sandbox REST Client Secret.
   - `CORS_ORIGINS`: Your Vercel frontend URL (e.g., `https://milestonepay-ai.vercel.app`).
7. Click **Apply**.

---

## Deployment Option B: Manual Service Configuration

### 1. Create Render Managed PostgreSQL
1. Click **New > PostgreSQL**.
2. **Name:** `milestonepay-db`
3. **Database:** `milestonepay`
4. **User:** `milestonepay_user`
5. **Region:** `Oregon (US West)`
6. **Plan:** `Starter` or `Standard` (avoid Free tier for production due to 30-day expiration and zero backups).
7. Copy the **Internal Database URL** once created.

### 2. Create Render Web Service
1. Click **New > Web Service**.
2. Connect your GitHub repository: `milestonepay-ai`.
3. Configure the following fields:
   - **Name:** `milestonepay-api`
   - **Region:** `Oregon (US West)` (must match database region).
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
   - **Health Check Path:** `/api/v1/health`

### 3. Configure Backend Environment Variables
Under the service **Environment** tab, add:

```env
APP_NAME=MilestonePay AI
ENVIRONMENT=production
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://milestonepay_user:<PASSWORD>@<INTERNAL_HOST>:5432/milestonepay
CORS_ORIGINS=https://milestonepay-ai.vercel.app,http://localhost:5173
JWT_SECRET_KEY=<GENERATE_A_64_CHAR_RANDOM_SECRET>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GEMINI_MODEL=gemini-2.5-flash
PAYMENT_PROVIDER=paypal
PAYPAL_MODE=sandbox
PAYPAL_API_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_CLIENT_ID=<YOUR_SANDBOX_CLIENT_ID>
PAYPAL_CLIENT_SECRET=<YOUR_SANDBOX_CLIENT_SECRET>
PAYPAL_WEBHOOK_ID=
PAYPAL_CURRENCY=USD
PAYPAL_REQUEST_TIMEOUT_SECONDS=20
MAX_UPLOAD_SIZE_MB=10
MAX_EVIDENCE_FILES=5
```

---

## 4. Database Migrations & Verification

Because the build command includes `alembic upgrade head`, all database migrations are applied automatically during deployment before the new service instance receives traffic.

To verify health and database connection after deployment:
```bash
curl -s https://milestonepay-api.onrender.com/api/v1/health/ready
```
Expected response:
```json
{"status":"ready","service":"milestonepay-api","database":"connected"}
```

---

## 5. Webhook Registration in PayPal

Once your backend is live at `https://milestonepay-api.onrender.com`:
1. Go to [PayPal Developer Dashboard > Sandbox Apps](https://developer.paypal.com/dashboard/applications/sandbox).
2. Click on your application.
3. Click **Add Webhook**.
4. Set **URL** to: `https://milestonepay-api.onrender.com/api/v1/webhooks/paypal`
5. Check event types:
   - `PAYMENT.CAPTURE.COMPLETED`
   - `PAYMENT.CAPTURE.DENIED`
   - `CHECKOUT.ORDER.APPROVED`
6. Save the webhook and copy the **Webhook ID**.
7. Set `PAYPAL_WEBHOOK_ID` in your Render Web Service environment variables.
