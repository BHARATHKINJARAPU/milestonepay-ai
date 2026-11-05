# MilestonePay AI

> **Work Smarter. Deliver Transparently. Get Paid Confidently.**

MilestonePay AI is an AI-powered freelance project and milestone payment management platform.

Freelancers often face unclear, unstructured project briefs. MilestonePay AI will convert vague requirements into clear project milestones, estimated budgets, deadlines, deliverables, and verifiable acceptance criteria. Clients and freelancers review and agree upon these milestones before work begins. Once deliverables are submitted, AI assists in evaluating submissions against the agreed requirements while clients retain authoritative final sign-off before milestone funds are released via PayPal.

This repository represents the **Day 1 Technical Foundation Setup**, establishing a robust full-stack architecture with React, TypeScript, Tailwind CSS v4, FastAPI, SQLAlchemy 2.x, and PostgreSQL.

---

## 1. Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │          React 19 + TypeScript         │
                      │             Tailwind CSS v4            │
                      │               Vite Client              │
                      │         (http://localhost:5173)        │
                      └───────────────────┬────────────────────┘
                                          │
                                          │ REST / JSON (Axios Client)
                                          │ CORS enabled
                                          ▼
                      ┌────────────────────────────────────────┐
                      │          Python FastAPI Backend        │
                      │             Uvicorn Server             │
                      │         (http://localhost:8000)        │
                      └───────────────────┬────────────────────┘
                                          │
                                          │ SQLAlchemy 2.x ORM
                                          │ Psycopg 3 Driver (SELECT 1)
                                          ▼
                      ┌────────────────────────────────────────┐
                      │          PostgreSQL 16 Database        │
                      │             Port 5432                  │
                      │          (Docker or Portable)          │
                      └────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Frontend
- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite 6
- **Styling:** Tailwind CSS v4 (via official `@tailwindcss/vite` plugin)
- **Routing:** React Router v7
- **Icons:** Lucide React
- **API Client:** Axios with centralized client configuration

### Backend
- **Language:** Python 3.12+ (tested on Python 3.13)
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **ORM:** SQLAlchemy 2.x
- **Database Driver:** Psycopg 3 (`psycopg[binary]`)
- **Settings Management:** Pydantic Settings & `python-dotenv`
- **Testing:** Pytest & HTTPX TestClient

### Database & Infrastructure
- **Database:** PostgreSQL 16
- **Containerization:** Docker Compose
- **Platform Support:** Windows PowerShell, macOS, Linux

---

## 3. Directory Structure

```
milestonepay-ai/
│
├── frontend/                               # React + TypeScript + Vite Client
│   ├── public/
│   │   └── favicon.svg                     # Custom SVG branding icon
│   ├── src/
│   │   ├── assets/                         # Static media assets
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx              # Responsive navigation bar
│   │   │   │   └── Footer.tsx              # Footer with brand & architecture notes
│   │   │   ├── sections/
│   │   │   │   ├── HeroSection.tsx         # Hero with milestone workflow showcase
│   │   │   │   ├── HowItWorks.tsx          # 3-Stage freelance workflow
│   │   │   │   └── FeaturesSection.tsx     # 6 Planned capabilities roadmap
│   │   │   └── status/
│   │   │       └── ConnectionStatus.tsx    # Live 3-tier diagnostics component
│   │   ├── lib/
│   │   │   └── api.ts                      # Centralized typed API client
│   │   ├── types/
│   │   │   └── health.ts                   # TypeScript interfaces for health/readiness
│   │   ├── App.tsx                         # Root application layout
│   │   ├── main.tsx                        # DOM mount entrypoint
│   │   └── index.css                       # Tailwind CSS v4 theme entrypoint
│   ├── .env.example                        # Frontend environment template
│   ├── .env                                # Local environment config (gitignored)
│   ├── .gitignore                          # Frontend git ignore rules
│   ├── index.html                          # HTML shell
│   ├── package.json                        # Frontend dependencies & scripts
│   ├── tsconfig.json                       # TypeScript compiler options
│   ├── tsconfig.node.json                  # Vite configuration TypeScript options
│   └── vite.config.ts                      # Vite configuration with Tailwind CSS v4
│
├── backend/                                # Python FastAPI Backend
│   ├── app/
│   │   ├── __init__.py                     # Package marker
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py                   # Central API v1 router
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       └── health.py               # Health & Database readiness routes
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py                   # Pydantic Settings & environment loader
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── session.py                  # SQLAlchemy engine & session dependency
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── base.py                     # Declarative ORM Base
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── health.py                   # Health & readiness Pydantic schemas
│   │   └── main.py                         # FastAPI application factory & CORS
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py                  # Pytest automated test suite
│   ├── .env.example                        # Backend environment template
│   ├── .env                                # Local environment config (gitignored)
│   ├── requirements.txt                    # Python dependencies
│   └── pytest.ini                          # Pytest configuration
│
├── docs/
│   └── day-1-checklist.md                  # Day 1 milestone verification checklist
│
├── docker-compose.yml                      # PostgreSQL 16 container definition
├── .gitignore                              # Root git ignore specification
└── README.md                               # Project documentation
```

---

## 4. Prerequisites

Before getting started, ensure the following tools are installed on your machine:

- **Node.js:** v20.x or v22.x+ LTS (verified on Node v24 LTS)
- **Python:** v3.12 or v3.13+
- **Docker & Docker Compose:** Optional for containerized PostgreSQL, or a local PostgreSQL 16 server
- **Git**

---

## 5. Quick Start (Windows PowerShell Guide)

Follow these step-by-step instructions to set up and launch MilestonePay AI.

### Step 1: Clone and Enter the Repository

```powershell
cd c:\Users\kinja\OneDrive\Desktop\milestonepay-ai
```

### Step 2: Configure Environment Variables

Create `.env` files from the provided templates:

**Backend:**
```powershell
Copy-Item backend\.env.example backend\.env
```
Default `backend/.env`:
```ini
APP_NAME=MilestonePay AI
ENVIRONMENT=development
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://milestonepay:milestonepay_dev_password@localhost:5432/milestonepay_dev
CORS_ORIGINS=http://localhost:5173
```

**Frontend:**
```powershell
Copy-Item frontend\.env.example frontend\.env
```
Default `frontend/.env`:
```ini
VITE_API_BASE_URL=http://localhost:8000
```

---

### Step 3: Start PostgreSQL

#### Option A: Using Docker Compose (Recommended)
If Docker is installed and running:
```powershell
docker compose up -d
```
Verify the container is healthy:
```powershell
docker compose ps
```

#### Option B: Using a Locally Installed PostgreSQL Instance
If Docker is not installed on your system:
1. Ensure your local PostgreSQL service is running on port `5432`.
2. Connect to PostgreSQL using `psql` or pgAdmin and run:
   ```sql
   CREATE USER milestonepay WITH PASSWORD 'milestonepay_dev_password';
   CREATE DATABASE milestonepay_dev OWNER milestonepay;
   GRANT ALL PRIVILEGES ON DATABASE milestonepay_dev TO milestonepay;
   ```
3. Alternatively, update `DATABASE_URL` in `backend/.env` to point to your existing PostgreSQL credentials:
   ```ini
   DATABASE_URL=postgresql+psycopg://<your_username>:<your_password>@localhost:5432/<your_database>
   ```

---

### Step 4: Backend Setup & Startup

1. Create a Python virtual environment:
   ```powershell
   cd backend
   python -m venv .venv
   ```

2. Activate the virtual environment:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   *(Note: If PowerShell complains about script execution policy, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

3. Install backend dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Run the automated Pytest test suite:
   ```powershell
   pytest
   ```

5. Start the FastAPI development server:
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

The backend is now live:
- Root info: [http://localhost:8000/](http://localhost:8000/)
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- API Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- Database Readiness: [http://localhost:8000/api/v1/health/ready](http://localhost:8000/api/v1/health/ready)

---

### Step 5: Frontend Setup & Startup

Open a second PowerShell terminal:

1. Navigate to the frontend directory:
   ```powershell
   cd c:\Users\kinja\OneDrive\Desktop\milestonepay-ai\frontend
   ```

2. Install npm dependencies:
   ```powershell
   cmd /c npm install
   ```

3. Verify production build:
   ```powershell
   cmd /c npm run build
   ```

4. Start the Vite development server:
   ```powershell
   cmd /c npm run dev
   ```

The frontend will be live at:
- Web App: [http://localhost:5173](http://localhost:5173)

---

## 6. API Endpoints Reference

| Method | Path | Summary | Expected Response | Description |
|---|---|---|---|---|
| `GET` | `/` | Root Info | `{"app": "MilestonePay AI", "version": "0.1.0", ...}` | Service entrypoint and endpoint navigation |
| `GET` | `/docs` | OpenAPI UI | Swagger HTML | Interactive documentation and sandbox |
| `GET` | `/api/v1/health` | Basic Health | `{"status": "ok", "service": "milestonepay-api"}` | Confirms FastAPI process is active |
| `GET` | `/api/v1/health/ready` | DB Readiness | `{"status": "ready", "service": "milestonepay-api", "database": "connected"}` | Executes `SELECT 1;` on PostgreSQL |

### Safe Error Handling
If PostgreSQL is unreachable, `GET /api/v1/health/ready` returns HTTP 503:
```json
{
  "detail": "Database service is unavailable. Please verify PostgreSQL connection."
}
```
*Database credentials, internal connection URLs, and stack traces are never exposed in responses.*

---

## 7. Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| `Execution_Policies` error in PowerShell | Windows restricts PowerShell scripts | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` or prefix commands with `cmd /c` (e.g. `cmd /c npm install`). |
| Database card shows `Unavailable` | PostgreSQL is not running or wrong port/password | Start Docker via `docker compose up -d` or verify local Postgres service on port 5432 with credentials in `backend/.env`. |
| Backend CORS error | Frontend port does not match `CORS_ORIGINS` | Verify `CORS_ORIGINS` in `backend/.env` includes `http://localhost:5173`. |
| Port 5432 already in use | An existing local PostgreSQL service is bound to 5432 | Stop the conflicting local service or adjust the mapped port in `docker-compose.yml` and `backend/.env`. |

---

## 8. Day 1 Non-Goals (Upcoming Scope)
The following features are purposefully planned for Days 2–5 and not implemented on Day 1:
- Gemini API integration & prompt engineering
- AI milestone generation & deliverable validation
- User registration and authentication
- PayPal Sandbox checkout & escrow payouts
- Project and milestone database CRUD tables

---

## 9. License & Attribution
MilestonePay AI — Built for the Hackathon. Day 1 Technical Foundation Setup.
