# MilestonePay AI

> **Work Smarter. Deliver Transparently. Get Paid Confidently.**

MilestonePay AI is an AI-powered freelance project and milestone payment management platform.

Freelancers often face unclear, unstructured project briefs. MilestonePay AI converts vague requirements into clear project milestones, estimated budgets, deadlines, deliverables, and verifiable acceptance criteria. Clients and freelancers review and agree upon these milestones before work begins. Once deliverables are submitted, AI assists in evaluating submissions against agreed requirements while clients retain authoritative final sign-off before milestone funds are released via PayPal.

This repository represents the **Day 1 & Day 2 Implementation**, featuring a production-ready full-stack architecture with React 19, TypeScript, Tailwind CSS v4, FastAPI, SQLAlchemy 2.x, PostgreSQL 16, Alembic migrations, Argon2 password security, and JWT role-based access.

---

## 1. Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │          React 19 + TypeScript         │
                      │             Tailwind CSS v4            │
                      │          Vite (Client / SPA)           │
                      │         (http://localhost:5173)        │
                      └───────────────────┬────────────────────┘
                                          │
                                          │ REST / JSON (Axios Client)
                                          │ Bearer JWT Authentication
                                          │ CORS enabled
                                          ▼
                      ┌────────────────────────────────────────┐
                      │          Python FastAPI Backend        │
                      │        Uvicorn ASGI Application        │
                      │         (http://localhost:8000)        │
                      │    Argon2id Hashing & JWT Validation   │
                      └───────────────────┬────────────────────┘
                                          │
                                          │ SQLAlchemy 2.x ORM
                                          │ Alembic Migration Engine
                                          │ Psycopg 3 Driver
                                          ▼
                      ┌────────────────────────────────────────┐
                      │          PostgreSQL 16 Database        │
                      │             Port 5432                  │
                      │    (Docker Compose or Portable PG)     │
                      └────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Frontend
- **Framework:** React 19 + TypeScript 5.7
- **Build Tool:** Vite 6
- **Styling:** Tailwind CSS v4 (via official `@tailwindcss/vite` plugin)
- **Routing:** React Router v7 (`BrowserRouter`, `ProtectedRoute`, `Routes`)
- **State & Context:** React Context API (`AuthContext`)
- **Icons:** Lucide React
- **API Client:** Axios with centralized Bearer token interceptor and safe error parsing

### Backend
- **Language:** Python 3.12+ (tested on Python 3.13)
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **ORM:** SQLAlchemy 2.x with DeclarativeBase
- **Database Driver:** Psycopg 3 (`psycopg[binary]`)
- **Security & Hashing:** Argon2id (`argon2-cffi`)
- **Token Authorization:** PyJWT (`pyjwt`, HMAC-SHA256)
- **Database Migrations:** Alembic 1.13+
- **Settings Management:** Pydantic Settings & `python-dotenv`
- **Validation:** Pydantic 2.x & `email-validator`
- **Testing:** Pytest & HTTPX TestClient (23 passing automated tests)

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
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── AuthFormField.tsx       # Reusable input with validation & icons
│   │   │   │   └── ProtectedRoute.tsx      # Route guard requiring authenticated session
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardHeader.tsx     # Header with role badge and quick action
│   │   │   │   ├── DashboardLayout.tsx     # Responsive shell with mobile drawer & sidebar
│   │   │   │   ├── Sidebar.tsx             # Workspace navigation & user profile
│   │   │   │   └── StatCard.tsx            # Metric cards with accent gradients
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx              # Public navbar with live auth links
│   │   │   │   └── Footer.tsx              # Footer with brand & roadmap attribution
│   │   │   ├── projects/
│   │   │   │   ├── CollaboratorForm.tsx    # Add registered freelancer/client by email
│   │   │   │   ├── ProjectCard.tsx         # Project preview card with status badges
│   │   │   │   └── ProjectForm.tsx         # Project creation and editing form
│   │   │   ├── sections/
│   │   │   │   ├── HeroSection.tsx         # Hero with CSS milestone workflow visualizer
│   │   │   │   ├── HowItWorks.tsx          # 3-Stage freelance workflow
│   │   │   │   └── FeaturesSection.tsx     # 6 Planned capabilities roadmap
│   │   │   └── status/
│   │   │       └── ConnectionStatus.tsx    # Live 3-tier diagnostics component
│   │   ├── context/
│   │   │   └── AuthContext.tsx             # Global authentication provider & state
│   │   ├── lib/
│   │   │   └── api.ts                      # Centralized typed API client with interceptor
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   │   ├── LoginPage.tsx           # Authentication page
│   │   │   │   └── RegisterPage.tsx        # Registration with Freelancer / Client selector
│   │   │   ├── dashboard/
│   │   │   │   └── DashboardPage.tsx       # Role-specific Client & Freelancer dashboards
│   │   │   ├── projects/
│   │   │   │   ├── CreateProjectPage.tsx   # Project brief creation
│   │   │   │   ├── ProjectDetailPage.tsx   # Project details, editing & collaborator link
│   │   │   │   └── ProjectsPage.tsx        # Project catalog with status filters & search
│   │   │   └── LandingPage.tsx             # Public landing page
│   │   ├── types/
│   │   │   ├── auth.ts                     # TypeScript interfaces for auth & users
│   │   │   ├── health.ts                   # Interfaces for health & readiness
│   │   │   └── project.ts                  # Interfaces for projects & members
│   │   ├── App.tsx                         # Root router & route definitions
│   │   ├── main.tsx                        # DOM mount entrypoint
│   │   ├── index.css                       # Tailwind CSS v4 entrypoint
│   │   └── vite-env.d.ts                   # Vite client typings
│   ├── .env.example                        # Frontend env template
│   ├── .env                                # Local frontend configuration (gitignored)
│   ├── .gitignore                          # Frontend git ignore rules
│   ├── index.html                          # HTML shell
│   ├── package.json                        # Dependencies & scripts
│   ├── tsconfig.json                       # TypeScript compiler options
│   ├── tsconfig.node.json                  # Vite configuration TypeScript options
│   └── vite.config.ts                      # Vite configuration with @tailwindcss/vite
│
├── backend/                                # Python FastAPI Backend
│   ├── alembic/                            # Alembic database migrations
│   │   ├── versions/
│   │   │   └── 1f2bb6bda680_create_users_projects_and_project_.py
│   │   ├── env.py                          # Dynamic Alembic environment
│   │   └── script.py.mako
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py                 # Registration, login, /me routes
│   │   │   │   ├── health.py               # Health & Database readiness routes
│   │   │   │   └── projects.py             # CRUD & collaboration routes
│   │   │   ├── deps.py                     # get_current_user security dependency
│   │   │   └── router.py                   # Central API v1 router
│   │   ├── core/
│   │   │   ├── config.py                   # Pydantic Settings & environment loader
│   │   │   └── security.py                 # Argon2id hashing & JWT token issuance
│   │   ├── db/
│   │   │   └── session.py                  # SQLAlchemy engine & session factory
│   │   ├── models/
│   │   │   ├── base.py                     # Declarative ORM Base
│   │   │   ├── enums.py                    # AccountType, ProjectStatus, MemberRole
│   │   │   ├── project.py                  # Project SQLAlchemy model
│   │   │   ├── project_member.py           # ProjectMember model with unique constraints
│   │   │   └── user.py                     # User model with unique indexed email
│   │   ├── schemas/
│   │   │   ├── auth.py                     # Pydantic schemas for registration & login
│   │   │   ├── health.py                   # Pydantic schemas for health & readiness
│   │   │   └── project.py                  # Pydantic schemas for projects & members
│   │   └── main.py                         # FastAPI application factory & CORS
│   ├── tests/
│   │   ├── test_auth.py                    # 7 automated authentication tests
│   │   ├── test_health.py                  # 6 automated health & preflight tests
│   │   └── test_projects.py                # 10 automated project management tests
│   ├── alembic.ini                         # Alembic configuration
│   ├── .env.example                        # Backend env template
│   ├── .env                                # Local backend configuration (gitignored)
│   ├── requirements.txt                    # Python dependencies
│   └── pytest.ini                          # Pytest configuration
│
├── docs/
│   ├── day-1-checklist.md                  # Day 1 technical foundation checklist
│   └── day-2-checklist.md                  # Day 2 authentication & projects checklist
│
├── docker-compose.yml                      # PostgreSQL 16 container definition
├── .gitignore                              # Root Git ignore specification
└── README.md                               # Project documentation
```

---

## 4. Database Models & Schema

### `users` Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | Primary Key | Random UUID (v4) |
| `full_name` | `VARCHAR(255)` | Not Null | User's full display name |
| `email` | `VARCHAR(255)` | Unique, Indexed, Not Null | Normalized lowercase email |
| `password_hash` | `VARCHAR(512)` | Not Null | Argon2id password hash |
| `account_type` | `VARCHAR(50)` | Not Null | `freelancer` or `client` |
| `is_active` | `BOOLEAN` | Default True | Active user flag |
| `created_at` | `TIMESTAMPTZ` | Server Default `NOW()` | Timestamp created |
| `updated_at` | `TIMESTAMPTZ` | Server Default `NOW()` | Timestamp last modified |

### `projects` Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | Primary Key | Random UUID (v4) |
| `title` | `VARCHAR(255)` | Not Null | Project title |
| `description` | `TEXT` | Not Null | Unstructured or structured brief |
| `budget_amount` | `NUMERIC(12, 2)` | Not Null | Total project budget |
| `currency` | `VARCHAR(3)` | Default `'USD'` | 3-letter currency code |
| `deadline` | `DATE` | Nullable | Target completion date |
| `status` | `VARCHAR(50)` | Default `'draft'`, Indexed | `draft`, `active`, `completed`, `archived` |
| `created_by_id` | `UUID` | Foreign Key (`users.id`) | Creator's user ID |
| `created_at` | `TIMESTAMPTZ` | Server Default `NOW()` | Timestamp created |
| `updated_at` | `TIMESTAMPTZ` | Server Default `NOW()` | Timestamp last modified |

### `project_members` Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | Primary Key | Random UUID (v4) |
| `project_id` | `UUID` | Foreign Key (`projects.id`) | Project reference |
| `user_id` | `UUID` | Foreign Key (`users.id`) | Member reference |
| `role` | `VARCHAR(50)` | Not Null | Member's project role (`client` or `freelancer`) |
| `joined_at` | `TIMESTAMPTZ` | Server Default `NOW()` | Timestamp linked |

**Table Constraints:**
- `uq_project_members_project_user`: `UNIQUE(project_id, user_id)` — A user cannot be added twice to the same project.
- `uq_project_members_project_role`: `UNIQUE(project_id, role)` — A project can have at most one client and one freelancer.

---

## 5. API Endpoints Reference

### Health & Diagnostics
| Method | Path | Summary | Expected Response | Description |
|---|---|---|---|---|
| `GET` | `/` | Root Info | `{"app": "MilestonePay AI", "version": "0.1.0", ...}` | Service entry point |
| `GET` | `/docs` | OpenAPI UI | Swagger HTML | Interactive API documentation |
| `GET` | `/api/v1/health` | Service Health | `{"status": "ok", "service": "milestonepay-api"}` | Confirms FastAPI process is active |
| `GET` | `/api/v1/health/ready` | DB Readiness | `{"status": "ready", "service": "milestonepay-api", "database": "connected"}` | Executes `SELECT 1;` on PostgreSQL |

### Authentication
| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | No | Registers user with unique email, Argon2 password hash, and account type (`client` or `freelancer`) |
| `POST` | `/api/v1/auth/login` | No | Authenticates user credentials and returns signed JWT access token |
| `GET` | `/api/v1/auth/me` | Yes (`Bearer`) | Returns current authenticated user profile |

### Project Management
| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/v1/projects` | Yes (`Bearer`) | Creates a project and automatically links creator as initial member |
| `GET` | `/api/v1/projects` | Yes (`Bearer`) | Returns only projects where authenticated user is a registered member (supports `?status=` filter) |
| `GET` | `/api/v1/projects/{id}` | Yes (`Bearer`) | Returns project details, metadata, and member profiles (403 for non-members) |
| `PATCH` | `/api/v1/projects/{id}` | Yes (`Bearer`) | Allows project creator to update title, description, budget, or deadline |
| `POST` | `/api/v1/projects/{id}/members` | Yes (`Bearer`) | Allows creator to add registered collaborator with complementary role by email |
| `PATCH` | `/api/v1/projects/{id}/status` | Yes (`Bearer`) | Allows creator to transition status (`draft` → `active` → `completed` → `archived`) |

---

## 6. Environment Configuration

### Backend (`backend/.env`)
```ini
APP_NAME=MilestonePay AI
ENVIRONMENT=development
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://milestonepay:milestonepay_dev_password@localhost:5432/milestonepay_dev
CORS_ORIGINS=http://localhost:5173
JWT_SECRET_KEY=milestonepay_dev_jwt_secret_key_849302194820194820194820
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Frontend (`frontend/.env`)
```ini
VITE_API_BASE_URL=http://localhost:8000
```

*Note: For the Day 2 MVP, the frontend uses session-scoped storage (`sessionStorage`) to store the access token. Production deployments should evaluate secure HttpOnly cookies with CSRF defense.*

---

## 7. Database Migrations (Alembic)

Alembic manages database schema evolution.

To generate a new migration after editing SQLAlchemy models:
```powershell
cd backend
.\.venv\Scripts\alembic.exe revision --autogenerate -m "describe changes"
```

To apply pending migrations to the PostgreSQL database:
```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
```

To roll back the last migration:
```powershell
cd backend
.\.venv\Scripts\alembic.exe downgrade -1
```

---

## 8. Quick Start (Windows PowerShell Guide)

### Terminal 1: Backend Server
```powershell
cd c:\Users\kinja\OneDrive\Desktop\milestonepay-ai\backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run migrations (if not already applied)
.\.venv\Scripts\alembic.exe upgrade head

# Start FastAPI development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: Frontend Client
```powershell
cd c:\Users\kinja\OneDrive\Desktop\milestonepay-ai\frontend

# Install dependencies (if needed)
cmd /c npm install

# Start Vite dev server
cmd /c npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173).  
The backend API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 9. Testing & Verification

### Run Backend Automated Tests (23 Passing Tests)
```powershell
cd c:\Users\kinja\OneDrive\Desktop\milestonepay-ai\backend
.\.venv\Scripts\python.exe -m pytest
```

### Run Frontend Production Build & Type Check
```powershell
cd c:\Users\kinja\OneDrive\Desktop\milestonepay-ai\frontend
cmd /c npm run build
```

---

## 10. Day 2 Non-Goals (Upcoming Scope)
The following features belong to later development stages and are purposefully not implemented in Day 2:
- Gemini API prompt chaining & milestone generation
- AI deliverable review against acceptance criteria
- File upload analysis & evidence verification
- PayPal SDK / Sandbox escrow holding & checkout
- Advanced email notification infrastructure
