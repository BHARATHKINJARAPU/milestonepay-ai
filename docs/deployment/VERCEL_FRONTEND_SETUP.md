# MilestonePay AI — Vercel Frontend Production Setup Guide

This guide details deploying the React 19 + TypeScript + Vite frontend of MilestonePay AI to the Vercel Edge Network.

---

## 1. Project Specifications

- **Target Platform:** Vercel (Edge CDN)
- **Framework Preset:** `Vite`
- **Root Directory:** `frontend`
- **Build Command:** `npm ci && npm run build` (or `npm run build`)
- **Output Directory:** `dist`
- **Node.js Version:** `20.x` or `22.x`

---

## 2. Vercel Project Import Steps

1. Log into your [Vercel Dashboard](https://vercel.com/).
2. Click **Add New... > Project**.
3. Select your GitHub repository: `milestonepay-ai` (owner: `BHARATHKINJARAPU`).
4. In the **Configure Project** screen:
   - **Project Name:** `milestonepay-ai`
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click **Edit** and select `frontend`.
   - **Build and Output Settings:**
     - Build Command: `npm run build` (or override with `npm ci && npm run build`)
     - Output Directory: `dist`
     - Install Command: `npm install` (or `npm ci`)

---

## 3. Environment Variables Configuration

In the **Environment Variables** panel in Vercel, add:

| Key | Value / Format | Purpose |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://milestonepay-api.onrender.com` | Deployed FastAPI backend HTTPS root (no trailing slash) |
| `VITE_PAYPAL_CLIENT_ID` | `<YOUR_PAYPAL_SANDBOX_CLIENT_ID>` | Public client ID for PayPal Smart Buttons SDK |

> [!CAUTION]
> Never set `GEMINI_API_KEY`, `PAYPAL_CLIENT_SECRET`, or `JWT_SECRET_KEY` in Vercel. Frontend variables are exposed in compiled client-side JavaScript. Only public client identifiers are permissible.

---

## 4. Single-Page Application (SPA) Routing & Security Headers

The repository includes [`frontend/vercel.json`](../../frontend/vercel.json) with pre-configured rewrites:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

This configuration ensures:
1. **Direct Route Refresh:** Visiting deep nested routes (such as `/projects/2d0f4e7f-676f-4ef4-8c49-95bfd1cceb16/milestones`) and reloading the browser will never return a Vercel 404, because requests are rewritten to `/index.html` for client-side routing.
2. **Clickjacking & MIME Protection:** `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff` prevent framing and MIME-confusion exploits.

---

## 5. Deployment Verification Checklist

Once Vercel reports **Deployment Complete**:
1. Open your assigned domain (e.g., `https://milestonepay-ai.vercel.app`).
2. Verify the landing page loads all CSS assets and iconography.
3. Open browser Developer Tools (`F12`) > **Console** and **Network** tabs.
4. Click **Create Free Account** and register a new Client account.
5. In the Network tab, verify the POST request:
   - Request URL: `https://milestonepay-api.onrender.com/api/v1/auth/register`
   - Status: `201 Created`
6. Verify successful redirect to the Dashboard (`/dashboard`).
7. Update `CORS_ORIGINS` in your Render backend with this exact Vercel URL.
