from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
import json
import logging
from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.enums import (
    AccountType,
    MemberRole,
    MilestonePaymentStatus,
    MilestoneStatus,
    PaymentProvider,
    PaymentStatus,
    PlanStatus,
    ProjectStatus,
    SubmissionStatus,
)
from app.models.milestone import Milestone
from app.models.milestone_plan import MilestonePlan
from app.models.milestone_submission import MilestoneSubmission
from app.models.payment import Payment
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.analytics import (
    CollaboratorOverviewItem,
    CurrencyAmount,
    DashboardAnalyticsResponse,
    DashboardMilestonesSummary,
    DashboardPaymentsSummary,
    DashboardProjectsSummary,
    PaymentAnalyticsResponse,
    PaymentTrendsItem,
    ProjectAiSummaryResponse,
    ReviewCenterItem,
    UpcomingDeadlineItem,
)
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Computes factual dashboard and financial analytics using PostgreSQL records."""

    def get_dashboard_analytics(
        self,
        db: Session,
        current_user: User,
    ) -> DashboardAnalyticsResponse:
        """Generate comprehensive role-specific dashboard metrics for client or freelancer."""
        user_role = current_user.account_type.value  # "client" or "freelancer"

        # 1. Fetch user's projects
        user_memberships = (
            db.query(ProjectMember)
            .filter(ProjectMember.user_id == current_user.id)
            .all()
        )
        project_ids = [m.project_id for m in user_memberships]

        projects = (
            db.query(Project)
            .options(
                joinedload(Project.members).joinedload(ProjectMember.user),
                joinedload(Project.milestone_plans).joinedload(MilestonePlan.milestones),
            )
            .filter(Project.id.in_(project_ids))
            .all()
            if project_ids
            else []
        )

        # 2. Project Statistics
        total_projects = len(projects)
        active_projects = sum(1 for p in projects if p.status == ProjectStatus.ACTIVE)
        completed_projects = sum(1 for p in projects if p.status == ProjectStatus.COMPLETED)
        
        # 3. Gather all relevant milestones across user projects
        all_milestones: List[Milestone] = []
        for p in projects:
            # Prefer active agreed plan, else latest plan
            agreed_plans = [plan for plan in p.milestone_plans if plan.status == PlanStatus.AGREED]
            chosen_plan = agreed_plans[0] if agreed_plans else (p.milestone_plans[0] if p.milestone_plans else None)
            if chosen_plan:
                all_milestones.extend(chosen_plan.milestones)

        milestones_by_status = defaultdict(int)
        for m in all_milestones:
            milestones_by_status[m.status.value] += 1

        milestones_summary = DashboardMilestonesSummary(
            total=len(all_milestones),
            not_started=milestones_by_status.get(MilestoneStatus.NOT_STARTED.value, 0),
            in_progress=milestones_by_status.get(MilestoneStatus.IN_PROGRESS.value, 0),
            submitted=milestones_by_status.get(MilestoneStatus.SUBMITTED.value, 0),
            revision_requested=milestones_by_status.get(MilestoneStatus.REVISION_REQUESTED.value, 0),
            approved=milestones_by_status.get(MilestoneStatus.APPROVED.value, 0),
        )

        # 4. Payments Financial Aggregation
        payments = (
            db.query(Payment)
            .filter(Payment.project_id.in_(project_ids))
            .all()
            if project_ids
            else []
        )

        # Group budgets by currency
        budget_by_currency = defaultdict(Decimal)
        for p in projects:
            budget_by_currency[p.currency] += p.budget_amount

        # Group approved milestone value (unpaid or pending) by currency
        approved_val_by_currency = defaultdict(Decimal)
        for m in all_milestones:
            if m.status == MilestoneStatus.APPROVED and m.payment_status != MilestonePaymentStatus.COMPLETED:
                approved_val_by_currency[m.currency] += m.amount

        # Group payments by provider and status
        paypal_completed = defaultdict(Decimal)
        mock_completed = defaultdict(Decimal)
        pending_payments = defaultdict(Decimal)
        failed_count = 0
        completed_count = 0

        for pay in payments:
            if pay.status == PaymentStatus.COMPLETED:
                completed_count += 1
                if pay.provider == PaymentProvider.PAYPAL:
                    paypal_completed[pay.currency] += pay.amount
                elif pay.provider == PaymentProvider.MOCK:
                    mock_completed[pay.currency] += pay.amount
            elif pay.status in {
                PaymentStatus.PENDING,
                PaymentStatus.ORDER_CREATED,
                PaymentStatus.PAYER_APPROVED,
                PaymentStatus.PROCESSING,
            }:
                pending_payments[pay.currency] += pay.amount
            elif pay.status == PaymentStatus.FAILED:
                failed_count += 1

        payments_summary = DashboardPaymentsSummary(
            total_budget_by_currency=[
                CurrencyAmount(currency=curr, amount=float(amt))
                for curr, amt in budget_by_currency.items()
            ],
            approved_value_by_currency=[
                CurrencyAmount(currency=curr, amount=float(amt))
                for curr, amt in approved_val_by_currency.items()
            ],
            completed_paypal_by_currency=[
                CurrencyAmount(currency=curr, amount=float(amt))
                for curr, amt in paypal_completed.items()
            ],
            completed_mock_by_currency=[
                CurrencyAmount(currency=curr, amount=float(amt))
                for curr, amt in mock_completed.items()
            ],
            pending_by_currency=[
                CurrencyAmount(currency=curr, amount=float(amt))
                for curr, amt in pending_payments.items()
            ],
            failed_count=failed_count,
            completed_count=completed_count,
        )

        # 5. Upcoming Deadlines (Ordered by due_date ascending)
        upcoming_deadlines: List[UpcomingDeadlineItem] = []
        for p in projects:
            for plan in p.milestone_plans:
                if plan.status == PlanStatus.AGREED:
                    for m in plan.milestones:
                        if m.status != MilestoneStatus.APPROVED and m.due_date:
                            dt = datetime(m.due_date.year, m.due_date.month, m.due_date.day, tzinfo=timezone.utc)
                            upcoming_deadlines.append(
                                UpcomingDeadlineItem(
                                    milestone_id=m.id,
                                    milestone_title=m.title,
                                    project_id=p.id,
                                    project_title=p.title,
                                    deadline=dt,
                                    status=m.status.value,
                                    suggested_budget=float(m.amount),
                                    currency=m.currency,
                                )
                            )
        upcoming_deadlines.sort(key=lambda x: x.deadline or datetime.max.replace(tzinfo=timezone.utc))

        # 6. Review Center (Actionable items for Client)
        review_center_items: List[ReviewCenterItem] = []
        if user_role == AccountType.CLIENT.value:
            for p in projects:
                # Milestone plans awaiting client review
                for plan in p.milestone_plans:
                    if plan.status == PlanStatus.PENDING_APPROVAL:
                        review_center_items.append(
                            ReviewCenterItem(
                                item_type="plan_review",
                                project_id=p.id,
                                project_title=p.title,
                                title=f"Milestone Plan v{plan.version} Awaiting Agreement",
                                subtitle=f"{len(plan.milestones)} milestones proposed ({p.currency} {float(plan.total_budget):,.2f})",
                                action_url=f"/projects/{p.id}/milestones",
                                created_at=plan.created_at,
                                amount=float(plan.total_budget),
                                currency=p.currency,
                            )
                        )

                # Approved milestones ready for payment
                agreed_plans = [plan for plan in p.milestone_plans if plan.status == PlanStatus.AGREED]
                if agreed_plans:
                    for m in agreed_plans[0].milestones:
                        if m.status == MilestoneStatus.APPROVED and m.payment_status != MilestonePaymentStatus.COMPLETED:
                            review_center_items.append(
                                ReviewCenterItem(
                                    item_type="pending_payment",
                                    project_id=p.id,
                                    project_title=p.title,
                                    milestone_id=m.id,
                                    milestone_title=m.title,
                                    title=f"Milestone Approved: '{m.title}' Ready for Payment",
                                    subtitle=f"Release agreed funds of {m.currency} {float(m.amount):,.2f} via PayPal Sandbox or Mock Provider",
                                    action_url=f"/projects/{p.id}/milestones/{m.id}/pay",
                                    created_at=datetime.now(timezone.utc),
                                    amount=float(m.amount),
                                    currency=m.currency,
                                )
                            )

            # Submissions submitted awaiting client review
            if all_milestones:
                milestone_ids = [m.id for m in all_milestones]
                submissions = (
                    db.query(MilestoneSubmission)
                    .options(joinedload(MilestoneSubmission.milestone).joinedload(Milestone.plan))
                    .filter(
                        MilestoneSubmission.milestone_id.in_(milestone_ids),
                        MilestoneSubmission.status == SubmissionStatus.SUBMITTED,
                    )
                    .all()
                )
                for sub in submissions:
                    p_id = sub.milestone.plan.project_id if sub.milestone and sub.milestone.plan else sub.milestone_id
                    p_title = next((p.title for p in projects if p.id == p_id), "Project")
                    review_center_items.append(
                        ReviewCenterItem(
                            item_type="submission_review",
                            project_id=p_id,
                            project_title=p_title,
                            milestone_id=sub.milestone_id,
                            milestone_title=sub.milestone.title if sub.milestone else "Deliverable",
                            submission_id=sub.id,
                            title=f"Deliverable Submitted for '{sub.milestone.title if sub.milestone else 'Milestone'}'",
                            subtitle=f"Attempt #{sub.attempt_number} submitted. AI evaluation ready for client verification.",
                            action_url=f"/projects/{p_id}/submissions/{sub.id}",
                            created_at=sub.created_at,
                            amount=float(sub.milestone.amount) if sub.milestone else None,
                            currency=sub.milestone.currency if sub.milestone else None,
                        )
                    )

        review_center_items.sort(key=lambda x: x.created_at, reverse=True)

        # 7. Collaborators Overview
        collaborators_dict: Dict[uuid.UUID, CollaboratorOverviewItem] = {}
        for p in projects:
            for member in p.members:
                if member.user_id != current_user.id and member.user:
                    u = member.user
                    if u.id not in collaborators_dict:
                        collaborators_dict[u.id] = CollaboratorOverviewItem(
                            user_id=u.id,
                            name=u.full_name,
                            email=u.email,
                            role=member.role.value,
                            project_count=1,
                            active_milestone_count=0,
                            latest_project_title=p.title,
                        )
                    else:
                        collaborators_dict[u.id].project_count += 1

        collaborators = list(collaborators_dict.values())

        # Projects requiring attention calculation
        attention_needed = len(review_center_items)

        projects_summary = DashboardProjectsSummary(
            total=total_projects,
            active=active_projects,
            completed=completed_projects,
            awaiting_review=len([item for item in review_center_items if item.item_type != "pending_payment"]),
            attention_needed=attention_needed,
        )

        return DashboardAnalyticsResponse(
            role=user_role,
            projects=projects_summary,
            milestones=milestones_summary,
            payments=payments_summary,
            upcoming_deadlines=upcoming_deadlines[:10],
            review_center=review_center_items[:15],
            collaborators=collaborators[:10],
        )

    def get_payment_analytics(
        self,
        db: Session,
        current_user: User,
    ) -> PaymentAnalyticsResponse:
        """Retrieve aggregated payment metrics and historical daily trend data."""
        user_memberships = (
            db.query(ProjectMember)
            .filter(ProjectMember.user_id == current_user.id)
            .all()
        )
        project_ids = [m.project_id for m in user_memberships]

        payments = (
            db.query(Payment)
            .filter(Payment.project_id.in_(project_ids))
            .order_by(Payment.created_at.asc())
            .all()
            if project_ids
            else []
        )

        projects = (
            db.query(Project)
            .filter(Project.id.in_(project_ids))
            .all()
            if project_ids
            else []
        )

        # Compute summary
        budget_by_currency = defaultdict(Decimal)
        for p in projects:
            budget_by_currency[p.currency] += p.budget_amount

        paypal_completed = defaultdict(Decimal)
        mock_completed = defaultdict(Decimal)
        pending_payments = defaultdict(Decimal)
        failed_count = 0
        completed_count = 0

        # Trends aggregate grouped by date string (YYYY-MM-DD)
        trends_map: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"paypal": Decimal(0), "mock": Decimal(0), "count": 0, "currency": "USD"}
        )

        for pay in payments:
            if pay.status == PaymentStatus.COMPLETED:
                completed_count += 1
                date_key = pay.completed_at.strftime("%Y-%m-%d") if pay.completed_at else pay.created_at.strftime("%Y-%m-%d")
                trends_map[date_key]["currency"] = pay.currency
                trends_map[date_key]["count"] += 1

                if pay.provider == PaymentProvider.PAYPAL:
                    paypal_completed[pay.currency] += pay.amount
                    trends_map[date_key]["paypal"] += pay.amount
                elif pay.provider == PaymentProvider.MOCK:
                    mock_completed[pay.currency] += pay.amount
                    trends_map[date_key]["mock"] += pay.amount
            elif pay.status in {
                PaymentStatus.PENDING,
                PaymentStatus.ORDER_CREATED,
                PaymentStatus.PAYER_APPROVED,
                PaymentStatus.PROCESSING,
            }:
                pending_payments[pay.currency] += pay.amount
            elif pay.status == PaymentStatus.FAILED:
                failed_count += 1

        payments_summary = DashboardPaymentsSummary(
            total_budget_by_currency=[
                CurrencyAmount(currency=c, amount=float(a)) for c, a in budget_by_currency.items()
            ],
            approved_value_by_currency=[],
            completed_paypal_by_currency=[
                CurrencyAmount(currency=c, amount=float(a)) for c, a in paypal_completed.items()
            ],
            completed_mock_by_currency=[
                CurrencyAmount(currency=c, amount=float(a)) for c, a in mock_completed.items()
            ],
            pending_by_currency=[
                CurrencyAmount(currency=c, amount=float(a)) for c, a in pending_payments.items()
            ],
            failed_count=failed_count,
            completed_count=completed_count,
        )

        trends: List[PaymentTrendsItem] = [
            PaymentTrendsItem(
                date=dt_str,
                currency=data["currency"],
                completed_paypal_amount=float(data["paypal"]),
                completed_mock_amount=float(data["mock"]),
                count=data["count"],
            )
            for dt_str, data in sorted(trends_map.items())
        ]

        return PaymentAnalyticsResponse(
            payments_summary=payments_summary,
            trends=trends,
        )

    def get_project_ai_summary(
        self,
        db: Session,
        project_id: uuid.UUID,
        current_user: User,
    ) -> ProjectAiSummaryResponse:
        """Generate an AI progress and health assessment for a project using Gemini, with deterministic fallback."""
        project = (
            db.query(Project)
            .options(
                joinedload(Project.members).joinedload(ProjectMember.user),
                joinedload(Project.milestone_plans).joinedload(MilestonePlan.milestones),
            )
            .filter(Project.id == project_id)
            .first()
        )

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        # Validate project membership
        is_member = any(m.user_id == current_user.id for m in project.members)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this project summary.",
            )

        # Factual computation from database
        agreed_plans = [p for p in project.milestone_plans if p.status == PlanStatus.AGREED]
        current_plan = agreed_plans[0] if agreed_plans else (project.milestone_plans[0] if project.milestone_plans else None)

        milestones = current_plan.milestones if current_plan else []
        total_milestones = len(milestones)
        approved_milestones = sum(1 for m in milestones if m.status == MilestoneStatus.APPROVED)
        submitted_milestones = sum(1 for m in milestones if m.status == MilestoneStatus.SUBMITTED)
        in_progress_milestones = sum(1 for m in milestones if m.status == MilestoneStatus.IN_PROGRESS)
        paid_milestones = sum(1 for m in milestones if m.payment_status == MilestonePaymentStatus.COMPLETED)

        completion_pct = int((approved_milestones / total_milestones * 100)) if total_milestones > 0 else 0

        # Payments total for project
        payments = db.query(Payment).filter(Payment.project_id == project_id).all()
        completed_payments_val = sum(p.amount for p in payments if p.status == PaymentStatus.COMPLETED)

        metrics = {
            "total_budget": float(project.budget_amount),
            "currency": project.currency,
            "total_milestones": total_milestones,
            "approved_milestones": approved_milestones,
            "submitted_milestones": submitted_milestones,
            "in_progress_milestones": in_progress_milestones,
            "paid_milestones": paid_milestones,
            "completion_percentage": completion_pct,
            "completed_payments": float(completed_payments_val),
            "plan_status": current_plan.status.value if current_plan else "no_plan",
        }

        # Attempt Gemini analysis if API key is present
        gemini_summary = None
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                prompt = (
                    f"Analyze this software project's factual metrics and provide an executive summary:\n"
                    f"Project Title: {project.title}\n"
                    f"Description: {project.description}\n"
                    f"Budget: {project.currency} {float(project.budget)}\n"
                    f"Total Milestones: {total_milestones}\n"
                    f"Approved Milestones: {approved_milestones}\n"
                    f"In Progress: {in_progress_milestones}\n"
                    f"Paid Milestones: {paid_milestones}\n"
                    f"Completion Rate: {completion_pct}%\n"
                    f"Plan Status: {metrics['plan_status']}\n\n"
                    f"Respond ONLY with a valid JSON object matching this structure:\n"
                    f"{{\n"
                    f'  "executive_summary": "1-2 sentence executive summary of project status",\n'
                    f'  "progress_assessment": "Assessment of delivery pace and quality",\n'
                    f'  "key_accomplishments": ["bullet 1", "bullet 2"],\n'
                    f'  "potential_risks": ["risk 1", "risk 2"],\n'
                    f'  "recommended_next_steps": ["step 1", "step 2"]\n'
                    f"}}"
                )

                client = gemini_service._get_client()
                response = client.models.generate_content(
                    model=gemini_service.model,
                    contents=prompt,
                )
                if response.text:
                    cleaned_text = response.text.strip()
                    if cleaned_text.startswith("```json"):
                        cleaned_text = cleaned_text[7:]
                    if cleaned_text.endswith("```"):
                        cleaned_text = cleaned_text[:-3]
                    gemini_summary = json.loads(cleaned_text.strip())
            except Exception as e:
                logger.warning("Gemini AI project summary generation failed gracefully: %s", e)

        if gemini_summary and isinstance(gemini_summary, dict) and "executive_summary" in gemini_summary:
            return ProjectAiSummaryResponse(
                project_id=project_id,
                generated_at=datetime.now(timezone.utc),
                is_ai_generated=True,
                executive_summary=gemini_summary.get("executive_summary", ""),
                progress_assessment=gemini_summary.get("progress_assessment", ""),
                key_accomplishments=gemini_summary.get("key_accomplishments", []),
                potential_risks=gemini_summary.get("potential_risks", []),
                recommended_next_steps=gemini_summary.get("recommended_next_steps", []),
                metrics=metrics,
            )

        # Deterministic fallback based strictly on factual database records
        accomplishments = []
        if approved_milestones > 0:
            accomplishments.append(f"{approved_milestones} of {total_milestones} milestones approved by client.")
        if paid_milestones > 0:
            accomplishments.append(f"{paid_milestones} milestone payments verified and settled ({project.currency} {float(completed_payments_val):,.2f}).")
        if not accomplishments:
            accomplishments.append("Project created and milestone framework established.")

        risks = []
        if total_milestones == 0:
            risks.append("No active milestone plan agreed yet.")
        elif in_progress_milestones == 0 and approved_milestones < total_milestones:
            risks.append("No active milestone currently in progress.")
        else:
            risks.append("Ensure timely submission of evidence for upcoming deliverable reviews.")

        next_steps = []
        if total_milestones == 0:
            next_steps.append("Generate and agree on the milestone plan.")
        elif submitted_milestones > 0:
            next_steps.append("Client review of submitted deliverables and Gemini evaluation.")
        elif approved_milestones > paid_milestones:
            next_steps.append("Client release of funds for approved milestone.")
        else:
            next_steps.append("Freelancer continue execution on next scheduled milestone.")

        return ProjectAiSummaryResponse(
            project_id=project_id,
            generated_at=datetime.now(timezone.utc),
            is_ai_generated=False,
            executive_summary=f"Project '{project.title}' is currently {completion_pct}% complete with {approved_milestones}/{total_milestones} milestones approved.",
            progress_assessment=f"Delivery is progressing with {in_progress_milestones} milestone(s) active and {paid_milestones} paid.",
            key_accomplishments=accomplishments,
            potential_risks=risks,
            recommended_next_steps=next_steps,
            metrics=metrics,
        )


analytics_service = AnalyticsService()
