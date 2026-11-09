# MilestonePay AI — PostgreSQL Database & Schema Integrity Test Report

**Date**: November 7, 2026  
**Auditor**: Principal Database Architect & Data Engineer  
**Database**: PostgreSQL 16 (psycopg v3, SQLAlchemy 2.0, Alembic)  
**Overall Status**: **100% PASS**

---

## 1. Schema Architecture & Entity Relationship Summary

The MilestonePay AI database consists of 12 core tables designed with strict relational integrity, UUID primary keys, and exact financial decimal precision:

```
                  ┌──────────────┐
                  │    users     │
                  └──────┬───────┘
                         │ 1:N
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌───────────┐ ┌──────────────┐ ┌───────────────┐
    │ projects  │ │project_member│ │ notifications │
    └─────┬─────┘ └──────────────┘ └───────────────┘
          │ 1:N
          ├─────────────────────────────┐
          ▼                             ▼
   ┌───────────────┐            ┌──────────────────┐
   │milestone_plans│            │project_activities│
   └──────┬────────┘            └──────────────────┘
          │ 1:N
          ▼
   ┌───────────────┐
   │  milestones   │
   └──────┬────────┘
          │ 1:N
          ├─────────────────────────────┐
          ▼                             ▼
   ┌───────────────┐            ┌──────────────────┐
   │  submissions  │            │     payments     │
   └──────┬────────┘            └────────┬─────────┘
          │ 1:N                          │ 1:N
     ┌────┴────────┐                     ▼
     ▼             ▼             ┌──────────────────┐
┌─────────┐ ┌───────────────┐   │  payment_events  │
│evidence │ │reviews (client│   └──────────────────┘
└─────────┘ │  & gemini ai) │
            └───────────────┘
```

---

## 2. Table Definitions & Key Constraints

| Table Name | Primary Key | Key Foreign Keys | Key Indexes & Constraints |
| :--- | :--- | :--- | :--- |
| `users` | `UUID` | None | `UNIQUE(email)`, index on `email`, `account_type` enum |
| `projects` | `UUID` | `created_by_id -> users.id` | `budget_amount NUMERIC(12,2)`, `currency VARCHAR(3)`, index on `status` |
| `project_members` | `UUID` | `project_id -> projects.id`, `user_id -> users.id` | `UNIQUE(project_id, user_id)`, `role` enum |
| `milestone_plans` | `UUID` | `project_id -> projects.id`, `created_by_id -> users.id` | `UNIQUE(project_id, version)`, `status` enum, `source` enum |
| `milestones` | `UUID` | `plan_id -> milestone_plans.id` | `amount NUMERIC(12,2)`, `budget_percentage NUMERIC(5,2)`, `order_index` |
| `milestone_plan_reviews`| `UUID` | `plan_id -> milestone_plans.id`, `reviewer_user_id -> users.id` | `decision` enum, `version` integer |
| `milestone_submissions` | `UUID` | `milestone_id -> milestones.id`, `submitted_by_id -> users.id` | `attempt_number` integer, `status` enum, `ai_review_status` enum |
| `submission_evidence` | `UUID` | `submission_id -> milestone_submissions.id` | `storage_key VARCHAR(255)`, `file_hash_sha256 VARCHAR(64)` |
| `submission_reviews` | `UUID` | `submission_id -> milestone_submissions.id`, `reviewer_user_id -> users.id` | `review_type` enum (client / gemini), `status` enum |
| `payments` | `UUID` | `milestone_id -> milestones.id`, `project_id -> projects.id`, `client_user_id -> users.id` | `amount NUMERIC(12,2)`, `provider` enum, `status` enum, `UNIQUE(provider_capture_id)` |
| `payment_events` | `UUID` | `payment_id -> payments.id` | `event_type VARCHAR(64)`, `event_source` enum, `created_at` |
| `paypal_webhook_events` | `UUID` | None | `UNIQUE(webhook_event_id)` (ensures webhook idempotency) |
| `notifications` | `UUID` | `user_id -> users.id` | `is_read` boolean, index on `(user_id, is_read)` |
| `project_activities` | `UUID` | `project_id -> projects.id`, `actor_user_id -> users.id` | `activity_type VARCHAR(64)`, `created_at` timestamp |

---

## 3. Alembic Migration Chain

The migration tree is sequential, non-branching, and current at head:
1. `1f2bb6bda680`: Initial schema (`users`, `projects`, `project_members`).
2. `37acafadee6a`: Milestone planning schema (`milestone_plans`, `milestones`, `milestone_plan_reviews`).
3. `b2d423d814cd`: Submissions and evidence schema (`milestone_submissions`, `submission_evidence`, `submission_reviews`).
4. `678c0e63c391`: Payment ledger schema (`payments`, `payment_events`, `paypal_webhook_events`).
5. `b95b944e495a` (Head): Audit and notifications schema (`notifications`, `project_activities`).

**Verification**:
Command `alembic current` executed cleanly and returned `b95b944e495a (head)`.

---

## 4. Financial Decimal Precision Verification

- All financial columns (`budget_amount`, `amount`, `budget_percentage`) are declared as PostgreSQL `NUMERIC` types, mapped to Python `Decimal`.
- Floating-point arithmetic is never used for currency balances.
- Cent-exact verification (`amount1 + amount2 == total_budget`) passed in automated tests and live audits.
- Safe transactions: SQLAlchemy sessions rollback automatically on exceptions, preventing partial writes.
