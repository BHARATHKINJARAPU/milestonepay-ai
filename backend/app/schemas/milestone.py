import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    MemberRole,
    MilestonePaymentStatus,
    MilestoneStatus,
    PlanGenerationSource,
    PlanStatus,
    ReviewDecision,
)
from app.schemas.auth import UserResponse


# ============================================================================
# STRUCTURED AI GENERATION SCHEMAS (Sent to / validated from Gemini)
# ============================================================================

class GeneratedMilestoneSchema(BaseModel):
    """Schema representing an individual milestone proposal produced by Gemini."""

    sequence_number: int = Field(..., ge=1, description="Sequential position of the milestone starting at 1")
    title: str = Field(..., min_length=3, max_length=255, description="Clear, professional milestone title")
    description: str = Field(..., min_length=10, description="Detailed explanation of the milestone scope")
    deliverables: List[str] = Field(..., min_length=1, description="List of concrete tangible deliverables")
    acceptance_criteria: List[str] = Field(..., min_length=1, description="Objective measurable criteria for completion")
    estimated_duration_days: int = Field(..., ge=1, le=365, description="Realistic estimated duration in business days")
    budget_percentage: float = Field(..., ge=0.0, le=100.0, description="Suggested allocation percentage between 0 and 100")
    dependencies: List[int] = Field(default_factory=list, description="List of prior sequence numbers this milestone depends on")


class GeminiProjectAnalysisSchema(BaseModel):
    """Top-level structured JSON schema required from Gemini."""

    project_summary: str = Field(..., min_length=10, description="Concise executive summary of project goals")
    project_complexity: str = Field(default="medium", description="Estimated project complexity: low, medium, or high")
    assumptions: List[str] = Field(default_factory=list, description="Explicit technical or business assumptions made")
    clarifying_questions: List[str] = Field(default_factory=list, description="Questions client or freelancer should clarify")
    risks: List[str] = Field(default_factory=list, description="Potential scope, technical, or timeline risks")
    needs_clarification: bool = Field(default=False, description="True if major requirements remain ambiguous")
    milestones: List[GeneratedMilestoneSchema] = Field(..., min_length=1, description="Structured milestones breakdown")


# ============================================================================
# API REQUEST SCHEMAS
# ============================================================================

class GenerateMilestonePlanRequest(BaseModel):
    """Payload to trigger AI milestone generation for a project."""

    additional_instructions: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional freelancer/client instructions to guide the AI decomposition",
    )


class MilestoneInput(BaseModel):
    """Input payload for a milestone in manual creation or updates."""

    id: Optional[uuid.UUID] = None
    sequence_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    deliverables: List[str] = Field(..., min_length=1)
    acceptance_criteria: List[str] = Field(..., min_length=1)
    estimated_duration_days: int = Field(default=7, gt=0)
    budget_percentage: Decimal = Field(..., gt=0, le=100)
    dependencies: List[int] = Field(default_factory=list)


class CreateManualPlanRequest(BaseModel):
    """Payload to create a milestone plan manually without AI."""

    project_summary: str = Field(..., min_length=10)
    milestones: List[MilestoneInput] = Field(..., min_length=1)
    assumptions: List[str] = Field(default_factory=list)
    clarifying_questions: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class UpdateMilestonePlanRequest(BaseModel):
    """Payload to edit a draft or revision-requested plan."""

    project_summary: Optional[str] = Field(None, min_length=10)
    milestones: Optional[List[MilestoneInput]] = Field(None, min_length=1)
    assumptions: Optional[List[str]] = None
    clarifying_questions: Optional[List[str]] = None
    risks: Optional[List[str]] = None


class RequestRevisionRequest(BaseModel):
    """Payload when requesting changes on a proposed plan."""

    comment: str = Field(..., min_length=5, max_length=3000, description="Specific feedback or changes requested")


# ============================================================================
# API RESPONSE SCHEMAS
# ============================================================================

class MilestoneResponse(BaseModel):
    """Individual milestone entity response."""

    id: uuid.UUID
    plan_id: uuid.UUID
    sequence_number: int
    title: str
    description: str
    deliverables: List[str]
    acceptance_criteria: List[str]
    estimated_duration_days: int
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    budget_percentage: Decimal
    amount: Decimal
    currency: str
    dependencies: List[int]
    status: MilestoneStatus = MilestoneStatus.NOT_STARTED
    payment_status: MilestonePaymentStatus = MilestonePaymentStatus.UNPAID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MilestonePlanReviewResponse(BaseModel):
    """Approval or change request review record."""

    id: uuid.UUID
    plan_id: uuid.UUID
    reviewer_user_id: uuid.UUID
    reviewer_role: MemberRole
    decision: ReviewDecision
    comment: Optional[str]
    created_at: datetime
    reviewer: UserResponse

    model_config = ConfigDict(from_attributes=True)


class MilestonePlanResponse(BaseModel):
    """Full milestone plan proposal response."""

    id: uuid.UUID
    project_id: uuid.UUID
    version: int
    status: PlanStatus
    project_summary: str
    total_amount: Decimal
    currency: str
    assumptions: List[str]
    clarifying_questions: List[str]
    risks: List[str]
    needs_clarification: bool
    generation_source: PlanGenerationSource
    ai_model: Optional[str]
    created_by_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    milestones: List[MilestoneResponse] = []
    reviews: List[MilestonePlanReviewResponse] = []

    model_config = ConfigDict(from_attributes=True)


class MilestonePlanListResponse(BaseModel):
    """List of all plan versions for a project."""

    plans: List[MilestonePlanResponse]
    total: int

