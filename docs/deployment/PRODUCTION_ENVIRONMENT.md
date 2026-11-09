# MilestonePay AI — Production Environment & Secret Configuration

This document specifies the complete production environment variable architecture, separation of concerns, and cross-origin security rules.

---

## 1. Environment Variable Architecture

```
                  +-----------------------------------+
                  |        Vercel (Frontend)          |
                  |                                   |
                  | VITE_API_BASE_URL (Render URL)    |
                  | VITE_PAYPAL_CLIENT_ID (Public ID) |
                  +-----------------------------------+
                                    |
                          HTTPS API Calls (CORS)
                                    v
                  +-----------------------------------+
                  |         Render (Backend)          |
                  |                                   |
                  | DATABASE_URL (Internal PG)        |
                  | CORS_ORIGINS (Vercel Domain)      |
                  | JWT_SECRET_KEY (HS256)            |
                  | GEMINI_API_KEY (Google AI Studio) |
                  | PAYPAL_CLIENT_SECRET (Backend-only|
                  | PAYPAL_CLIENT_ID                  |
                  | PAYPAL_WEBHOOK_ID                 |
                  | UPLOAD_DIR (Persistent Disk)      |
                  +-----------------------------------+
                                    |
                           Private Wire (TLS)
                                    v
                  +-----------------------------------+
                  |      Render (PostgreSQL 16)       |
                  |  Persistent SSD + Daily Backups   |
                  +-----------------------------------+
```

---

## 2. Complete Environment Matrix

| Variable | Scope | Provider | Classification | Example / Description |
| :--- | :--- | :--- | :--- | :--- |
| `APP_NAME` | Backend | Render | Public | `MilestonePay AI` |
| `ENVIRONMENT` | Backend | Render | Public | `production` |
| `API_V1_PREFIX` | Backend | Render | Public | `/api/v1` |
| `DATABASE_URL` | Backend | Render | **Secret** | `postgresql+psycopg://user:pass@dpg-xxx:5432/milestonepay` |
| `CORS_ORIGINS` | Backend | Render | Public | `https://milestonepay-ai.vercel.app` |
| `JWT_SECRET_KEY` | Backend | Render | **Secret** | 64-char random hex string (`openssl rand -hex 32`) |
| `JWT_ALGORITHM` | Backend | Render | Public | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | Render | Public | `120` |
| `GEMINI_API_KEY` | Backend | Render | **Secret** | Google Gemini API key from AI Studio |
| `GEMINI_MODEL` | Backend | Render | Public | `gemini-2.5-flash` |
| `PAYMENT_PROVIDER` | Backend | Render | Public | `paypal` |
| `PAYPAL_MODE` | Backend | Render | Public | `sandbox` |
| `PAYPAL_API_BASE_URL` | Backend | Render | Public | `https://api-m.sandbox.paypal.com` |
| `PAYPAL_CLIENT_ID` | Backend | Render | Sensitive | Sandbox REST Client ID |
| `PAYPAL_CLIENT_SECRET` | Backend | Render | **Secret** | Sandbox REST Client Secret |
| `PAYPAL_WEBHOOK_ID` | Backend | Render | Sensitive | Registered PayPal Webhook ID |
| `PAYPAL_CURRENCY` | Backend | Render | Public | `USD` |
| `UPLOAD_DIR` | Backend | Render | Internal | `/var/data/uploads` (Render disk mount path) |
| `MAX_UPLOAD_SIZE_MB` | Backend | Render | Public | `10` |
| `MAX_EVIDENCE_FILES` | Backend | Render | Public | `5` |
| `VITE_API_BASE_URL` | Frontend | Vercel | Public | `https://milestonepay-api.onrender.com` |
| `VITE_PAYPAL_CLIENT_ID` | Frontend | Vercel | Public | Sandbox REST Client ID (identical to backend) |

---

## 3. PayPal Webhook Configuration in Production

Webhooks allow PayPal to notify MilestonePay AI asynchronously when transactions are captured, refunded, or voided.

### Registration Procedure
1. Log into [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/).
2. Select your Sandbox REST application.
3. In the **Webhooks** section, click **Add Webhook**.
4. Set the **Webhook URL** to your live Render backend:
   ```
   https://milestonepay-api.onrender.com/api/v1/webhooks/paypal
   ```
5. Check the following event subscriptions:
   - `Payment capture completed` (`PAYMENT.CAPTURE.COMPLETED`)
   - `Payment capture denied` (`PAYMENT.CAPTURE.DENIED`)
   - `Checkout order approved` (`CHECKOUT.ORDER.APPROVED`)
6. Click **Save**.
7. Copy the generated **Webhook ID** (e.g. `4JH8938174129841B`).
8. Add it to your Render Web Service environment variables:
   ```
   PAYPAL_WEBHOOK_ID=4JH8938174129841B
   ```

---

## 4. Cross-Origin Resource Sharing (CORS) Rules

In production:
- The backend strictly enforces `allow_credentials=True`.
- The browser requires that the `Access-Control-Allow-Origin` header match the requesting origin exactly (wildcard `*` is rejected by browsers when credentials/cookies are permitted).
- In [`backend/app/core/config.py`](../../backend/app/core/config.py), `CORS_ORIGINS` accepts a comma-separated list of origins.
- Set `CORS_ORIGINS` in Render:
  ```
  CORS_ORIGINS=https://milestonepay-ai.vercel.app,http://localhost:5173
  ```
