# MilestonePay AI — Vercel Frontend Deployment Guide

This guide walks through deploying the React + TypeScript + Vite frontend of MilestonePay AI to the Vercel Edge Network.

---

## 1. Project Setup in Vercel

1. Log into your [Vercel Dashboard](https://vercel.com/).
2. Click **Add New... > Project**.
3. Select your GitHub repository: `milestonepay-ai`.
4. In the **Configure Project** screen, configure the following settings:
   - **Project Name:** `milestonepay-ai`
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click **Edit** and choose `frontend`.

---

## 2. Build & Output Settings

Vercel will detect Vite automatically. Verify the defaults match:
- **Build Command:** `npm run build` (executes `tsc -b && vite build`)
- **Output Directory:** `dist`
- **Install Command:** `npm install`

The repository already includes `frontend/vercel.json` which provides:
- Single Page Application (SPA) fallback rewrite: `/(.*) -> /index.html` (preventing 404s when refreshing nested React Router routes).
- Security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`).

---

## 3. Environment Variables Configuration

In the Vercel **Environment Variables** section, add:

| Name | Value | Purpose |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://milestonepay-api.onrender.com` | Live FastAPI backend endpoint (no trailing slash). |
| `VITE_PAYPAL_CLIENT_ID` | `<YOUR_SANDBOX_CLIENT_ID>` | Public PayPal Sandbox Client ID for frontend button rendering. |

> [!WARNING]
> Do NOT add `GEMINI_API_KEY`, `PAYPAL_CLIENT_SECRET`, or database credentials to Vercel. Frontend environment variables prefixed with `VITE_` are embedded in publicly accessible JavaScript client bundles.

---

## 4. Deploy & Connect to Backend

1. Click **Deploy**.
2. Once the build finishes (typically ~45 seconds), copy your assigned production domain (e.g., `https://milestonepay-ai.vercel.app`).
3. Return to your Render backend service dashboard:
   - Under **Environment**, update `CORS_ORIGINS` to include your new Vercel domain:
     ```
     CORS_ORIGINS=https://milestonepay-ai.vercel.app,http://localhost:5173
     ```
   - Click **Save Changes** (Render will automatically redeploy the backend with the new CORS origin).

---

## 5. Verification Checklist

- [ ] Open your deployed Vercel domain in an incognito window.
- [ ] Verify the landing page loads with modern styling and responsive layout.
- [ ] Register a new test Client account.
- [ ] Create a project and confirm the API calls succeed with HTTP 200/201.
- [ ] Refresh a deep route (e.g., `/projects/<id>/milestones`) to verify SPA rewrite works without a 404 error.
