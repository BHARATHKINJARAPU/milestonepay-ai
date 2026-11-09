# MilestonePay AI — Render PostgreSQL Production Setup Guide

This guide details the procedure for provisioning and configuring a **paid persistent Render PostgreSQL** database for MilestonePay AI.

---

## 1. Plan & Tier Selection

Render offers several managed PostgreSQL plans:
- **Free Tier:** Expires after 30 days, has no automated backups, and spins down. **Not suitable for production.**
- **Starter Tier ($7/month):** 256 MB RAM, 1 shared CPU, 10 GB persistent SSD storage, automated daily backups. Suitable for staging and early production.
- **Standard Tier ($20/month):** 1 GB RAM, 1 shared CPU, 20 GB persistent SSD storage, automated daily backups with point-in-time recovery. **Recommended for production.**

---

## 2. Provisioning Steps (Render Dashboard)

1. Navigate to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** in the top navigation bar and select **PostgreSQL**.
3. Configure the following database properties:
   - **Name:** `milestonepay-db`
   - **Database:** `milestonepay`
   - **User:** `milestonepay_user`
   - **Region:** `Oregon (US West)` *(Crucial: must match the region selected for your Render Web Service to enable zero-latency private internal networking).*
   - **PostgreSQL Version:** `16`
   - **Instance Type:** Select **Starter** or **Standard** (paid tier).
4. Click **Create Database**.

---

## 3. Connection Strings & Driver Configuration

Render generates two connection strings:

### A. Internal Database URL (Recommended for Backend)
- **Format:** `postgresql://milestonepay_user:<PASSWORD>@dpg-<ID>:5432/milestonepay`
- **Scope:** Accessible **only** by Render services located within the same region (`Oregon`).
- **Benefits:** Free internal bandwidth, lower latency, and traffic stays within Render's private virtual network.

### B. External Database URL (For Local Migrations & Remote DBA Tools)
- **Format:** `postgresql://milestonepay_user:<PASSWORD>@dpg-<ID>.<REGION>.render.com/milestonepay?sslmode=require`
- **Scope:** Accessible from anywhere on the public internet. Enforces TLS encryption via `sslmode=require`.

### C. SQLAlchemy 2 + Psycopg 3 Compatibility
In MilestonePay AI, our settings validator automatically normalizes `postgres://` and `postgresql://` schemes to `postgresql+psycopg://`. You can paste Render's connection string directly into `DATABASE_URL` without manual editing.

---

## 4. Connection Pooling & Production Settings

In [`backend/app/db/session.py`](../../backend/app/db/session.py), the SQLAlchemy synchronous engine is pre-configured with robust production pooling parameters:
- `pool_pre_ping=True`: Tests connections with a lightweight `SELECT 1` ping before handing them to requests, transparently discarding stale/terminated connections.
- `pool_size=5`: Default pool of persistent database connections.
- `max_overflow=10`: Allows up to 15 concurrent database connections during traffic spikes.
- `pool_timeout=10`: Rejects requests after 10 seconds if no connections are available, preventing request queuing cascading failures.

---

## 5. Production Migration Execution Procedure

Migrations must be run on the production database to create all tables and indexes.

### Automated Migrations (Recommended)
When deploying via `render.yaml` or Render Web Service build commands, migrations run automatically during deployment:
```bash
pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
```

### Manual Remote Migration (Alternative)
If you prefer executing migrations from your local development machine against the production database:
1. Copy the **External Database URL** from the Render Dashboard.
2. In PowerShell, execute:
   ```powershell
   cd backend
   $env:DATABASE_URL="postgresql+psycopg://milestonepay_user:<PASSWORD>@dpg-<ID>.<REGION>.render.com/milestonepay?sslmode=require"
   .\.venv\Scripts\python.exe -m alembic upgrade head
   ```
3. Verify current revision:
   ```powershell
   .\.venv\Scripts\python.exe -m alembic current
   # Expected output: b95b944e495a (head)
   ```

---

## 6. Verification Queries

Connect to your database via Render's **Connect > Web Shell** or using `psql`:
```sql
-- Check that all 11 core tables exist
SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';

-- Expected tables:
-- alembic_version, users, projects, project_members, milestone_plans,
-- milestone_plan_reviews, milestones, milestone_submissions,
-- submission_evidence, submission_reviews, payments, payment_events,
-- paypal_webhook_events, notifications, project_activities
```
