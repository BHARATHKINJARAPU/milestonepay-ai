from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict


class CurrencyAmount(BaseModel):
    """Monetary amount paired with its ISO currency code."""

    currency: str
    amount: float

    model_config = ConfigDict(from_attributes=True)


class DashboardProjectsSummary(BaseModel):
    """Project statistics summary."""

    total: int
    active: int
    completed: int
    awaiting_review: int
    attention_needed: int


class DashboardMilestonesSummary(BaseModel):
    """Milestone execution status counts."""

    total: int
    not_started: int
    in_progress: int
    submitted: int
    revision_requested: int
    approved: int


class DashboardPaymentsSummary(BaseModel):
    """Factual financial insights grouped by currency and provider category."""

    total_budget_by_currency: List[CurrencyAmount]
    approved_value_by_currency: List[CurrencyAmount]
    completed_paypal_by_currency: List[CurrencyAmount]
    completed_mock_by_currency: List[CurrencyAmount]
    pending_by_currency: List[CurrencyAmount]
    failed_count: int
    completed_count: int


class UpcomingDeadlineItem(BaseModel):
    """Milestone with impending deadline for freelancer planning."""

    milestone_id: uuid.UUID
    milestone_title: str
    project_id: uuid.UUID
    project_title: str
    deadline: Optional[datetime] = None
    status: str
    suggested_budget: float
    currency: str


class ReviewCenterItem(BaseModel):
    """Actionable item requiring client or collaborator attention."""

    item_type: str  # 'plan_review' | 'submission_review' | 'pending_payment'
    project_id: uuid.UUID
    project_title: str
    milestone_id: Optional[uuid.UUID] = None
    milestone_title: Optional[str] = None
    submission_id: Optional[uuid.UUID] = None
    title: str
    subtitle: str
    action_url: str
    created_at: datetime
    amount: Optional[float] = None
    currency: Optional[str] = None


class CollaboratorOverviewItem(BaseModel):
    """Overview of active client or freelancer collaborators."""

    user_id: uuid.UUID
    name: str
    email: str
    role: str
    project_count: int
    active_milestone_count: int
    latest_project_title: Optional[str] = None


class DashboardAnalyticsResponse(BaseModel):
    """Comprehensive dashboard payload tailored to current user role."""

    role: str
    projects: DashboardProjectsSummary
    milestones: DashboardMilestonesSummary
    payments: DashboardPaymentsSummary
    upcoming_deadlines: List[UpcomingDeadlineItem]
    review_center: List[ReviewCenterItem]
    collaborators: List[CollaboratorOverviewItem]


class PaymentTrendsItem(BaseModel):
    """Historical completed payment aggregate by date."""

    date: str
    currency: str
    completed_paypal_amount: float
    completed_mock_amount: float
    count: int


class PaymentAnalyticsResponse(BaseModel):
    """Detailed analytics on platform financial operations."""

    payments_summary: DashboardPaymentsSummary
    trends: List[PaymentTrendsItem]


class ProjectAiSummaryResponse(BaseModel):
    """Structured AI summary and health check for a specific project."""

    project_id: uuid.UUID
    generated_at: datetime
    is_ai_generated: bool
    executive_summary: str
    progress_assessment: str
    key_accomplishments: List[str]
    potential_risks: List[str]
    recommended_next_steps: List[str]
    metrics: Dict[str, Any]

