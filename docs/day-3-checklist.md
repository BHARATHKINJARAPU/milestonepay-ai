# MilestonePay AI — Day 3 Implementation Checklist
**Gemini AI Milestone Generator & Bilateral Agreement System**

## 1. Google Gemini AI Integration
- [x] Installed official `google-genai` Python SDK (`2.34.0`) in `backend/requirements.txt`.
- [x] Environment configuration in `backend/app/core/config.py` (`GEMINI_API_KEY`, `GEMINI_MODEL=gemini-2.5-flash`).
- [x] AI integration service isolated in `backend/app/services/gemini_service.py`.
- [x] Structured output enforcement via `response_schema=GeminiProjectAnalysisSchema` and `response_mime_type="application/json"`.
- [x] Low temperature setting (`0.2`) for deterministic structural decomposition.
- [x] Sensitive prompt injection defense and input sanitization in `backend/app/services/milestone_generator.py`.
- [x] Informative error handling for missing API keys or upstream model parse failures (HTTP 400 with actionable messages).

## 2. Deterministic Financial Math & Rounding Guarantees
- [x] All monetary calculations strictly performed in backend Python using `Decimal` (never client-side JavaScript floats).
- [x] Sum of milestone amounts guaranteed to match project total budget to the exact cent (`sum(amounts) == total_budget`).
- [x] Fractional budget rounding discrepancies deterministically resolved on final milestone.
- [x] Percentage allocations normalized and verified to equal 100.0%.

## 3. Database Architecture & Alembic Migrations
- [x] Table `milestone_plans`:
  - `id` (UUID PK), `project_id` (FK projects.id, ondelete CASCADE), `version` (int)
  - `status` (`draft`, `pending_approval`, `revision_requested`, `agreed`)
  - `project_summary` (text), `total_amount` (numeric 12,2), `currency` (char 3)
  - `assumptions` (JSONB), `clarifying_questions` (JSONB), `risks` (JSONB), `needs_clarification` (bool)
  - `generation_source` (`ai`, `manual`), `ai_model` (string nullable), `created_by_id` (FK users.id)
  - Timestamps `created_at`, `updated_at`
  - Constraint: `uq_milestone_plans_project_version`
- [x] Table `milestones`:
  - `id` (UUID PK), `plan_id` (FK milestone_plans.id, ondelete CASCADE), `sequence_number` (int)
  - `title`, `description`, `deliverables` (JSONB), `acceptance_criteria` (JSONB)
  - `estimated_duration_days`, `start_date`, `due_date`, `budget_percentage`, `amount`, `currency`
  - `dependencies` (JSONB array of sequence numbers)
  - Constraint: `uq_milestones_plan_sequence`
- [x] Table `milestone_plan_reviews`:
  - `id` (UUID PK), `plan_id` (FK milestone_plans.id, ondelete CASCADE), `reviewer_user_id` (FK users.id)
  - `reviewer_role` (`client`, `freelancer`), `decision` (`approved`, `changes_requested`), `comment` (text)
  - Constraint: `uq_plan_reviews_plan_reviewer`
- [x] Alembic migration `37acafadee6a_create_milestone_plans_milestones_and_.py` applied successfully to PostgreSQL.

## 4. Bilateral Two-Party Agreement Workflow
- [x] Submitting for approval requires both a `client` and `freelancer` to be linked members of the project.
- [x] Content locking: plans in `pending_approval` or `agreed` cannot be edited.
- [x] Explicit mutual approval: Plan transitions to `agreed` only when both client and freelancer approve the exact proposal version.
- [x] Project state auto-activation: Project advances from `draft` to `active` when the milestone plan is agreed.
- [x] Revision requests: Either party can request revisions with mandatory feedback comments; plan transitions to `revision_requested` and unlocks for editing.

## 5. API Endpoints (`/api/v1/projects/{project_id}/milestone-plans`)
- [x] `POST /generate`: Generates structured milestone proposal via Gemini AI.
- [x] `POST /manual`: Manually creates a custom milestone plan version.
- [x] `GET /`: Lists all plan versions ordered by version descending.
- [x] `GET /{plan_id}`: Retrieves single plan details with milestones and review decisions.
- [x] `PATCH /{plan_id}`: Edits summary, assumptions, or milestones (draft/revision_requested only).
- [x] `POST /{plan_id}/submit-for-approval`: Submits proposal for bilateral review.
- [x] `POST /{plan_id}/approve`: Records user approval and sets `agreed` if both parties approve.
- [x] `POST /{plan_id}/request-revision`: Submits revision feedback and unlocks plan.

## 6. Frontend Components & Pages
- [x] `MilestoneCard.tsx`: Sequence badge, deliverables, criteria, budget percentage, dates, dependencies.
- [x] `MilestoneBudgetSummary.tsx`: Multi-segment allocation bar and exact 100% cent-match badge.
- [x] `ClarificationPanel.tsx`: Gemini scope assumptions, clarifying questions, and risk alerts.
- [x] `PlanApprovalPanel.tsx`: Two-party approval indicators, revision comment history, and role-based action buttons.
- [x] `MilestoneTimeline.tsx`: Sequential roadmap view with duration and dependency connectors.
- [x] `MilestoneGeneratorModal.tsx`: Generative AI dialog with custom prompt instructions and loading states.
- [x] `MilestoneEditorModal.tsx`: Modal for editing individual milestone deliverables and criteria.
- [x] `MilestoneWorkspacePage.tsx`: Dedicated workspace (`/projects/:projectId/milestones`) with version selector.
- [x] `ProjectDetailPage.tsx`: Embedded AI Milestone Plan card with direct navigation into workspace.

## 7. Verification & Automated Testing
- [x] 14 new Day 3 unit/integration tests in `backend/tests/test_milestones.py`.
- [x] Total 37 backend tests passing (`pytest -v`): 100% pass rate.
- [x] Frontend TypeScript compilation and production build verified (`tsc -b && vite build`): Zero errors.
- [x] Live end-to-end integration verified against running PostgreSQL and FastAPI server.

