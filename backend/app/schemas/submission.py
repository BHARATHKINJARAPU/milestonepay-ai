import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import AIReviewStatus, ClientSubmissionDecision, CriterionEvaluationStatus, SubmissionStatus
from app.schemas.auth import UserResponse


# ============================================================================
# GEMINI STRUCTURED OUTPUT SCHEMAS
# ============================================================================

class CriterionEvaluationOutputSchema(BaseModel):
    """Evaluation of an individual milestone acceptance criterion by Gemini AI."""

    criterion_id: int = Field(..., description="Sequence number of the criterion (1-indexed)")
    criterion_text: str = Field(..., description="Exact text of the acceptance criterion evaluated")
    status: CriterionEvaluationStatus = Field(
        ...,
        description="Assessment: met, partially_met, not_demonstrated, or unable_to_assess",
    )
    explanation: str = Field(
        ...,
        min_length=5,
        description="Detailed evidence-based justification for this status",
    )
    supporting_evidence_ids: List[str] = Field(
        default_factory=list,
        description="Identifiers or filenames of supporting evidence items",
    )
    missing_information: Optional[str] = Field(
        default=None,
        description="Specific gaps or unverified elements preventing full verification",
    )


class GeminiDeliverableEvaluationSchema(BaseModel):
    """Structured report produced by Gemini AI analyzing deliverable submission evidence."""

    overall_summary: str = Field(
        ...,
        min_length=10,
        description="Objective executive summary of the submitted deliverable work",
    )
    criterion_evaluations: List[CriterionEvaluationOutputSchema] = Field(
        ...,
        min_length=1,
        description="Individual criterion-by-criterion assessment against agreed requirements",
    )
    identified_gaps: List[str] = Field(
        default_factory=list,
        description="Specific deliverables or acceptance elements missing or incomplete",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Concrete, actionable recommendations for remediation",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Disclosures of evidence format limits, unverified claims, or unreadable files",
    )
    areas_for_human_verification: List[str] = Field(
        default_factory=list,
        description="Items requiring client live inspection (e.g. backend logic, URLs)",
    )


# ============================================================================
# API REQUEST SCHEMAS
# ============================================================================

class CreateSubmissionRequest(BaseModel):
    """Payload to initiate a new milestone submission attempt (draft)."""

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Detailed description of the completed deliverable work",
    )
    notes: Optional[str] = Field(
        None,
        max_length=5000,
        description="Implementation details, architecture decisions, or testing notes",
    )
    demonstration_url: Optional[str] = Field(
        None,
        max_length=2048,
        description="Optional live demo or preview URL (displayed only, never crawled)",
    )


class ClientReviewRequest(BaseModel):
    """Payload for client approval or revision request on a submitted milestone."""

    decision: ClientSubmissionDecision = Field(
        ...,
        description="Client decision: 'approved' or 'revision_requested'",
    )
    comment: Optional[str] = Field(
        None,
        max_length=3000,
        description="Feedback or revision requirements. Mandatory if requesting changes.",
    )

    @field_validator("comment")
    @classmethod
    def validate_comment_for_revisions(cls, v: Optional[str], info) -> Optional[str]:
        decision = info.data.get("decision")
        if decision == ClientSubmissionDecision.REVISION_REQUESTED:
            if not v or len(v.strip()) < 5:
                raise ValueError("A clear comment (minimum 5 characters) is required when requesting revisions.")
        return v.strip() if v else None


# ============================================================================
# API RESPONSE SCHEMAS
# ============================================================================

class SubmissionEvidenceResponse(BaseModel):
    """Uploaded verification evidence artifact metadata."""

    id: uuid.UUID
    submission_id: uuid.UUID
    uploaded_by_id: uuid.UUID
    original_filename: str
    media_type: str
    file_size_bytes: int
    sha256_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AISubmissionReviewResponse(BaseModel):
    """AI evaluation audit report."""

    id: uuid.UUID
    submission_id: uuid.UUID
    review_version: int
    overall_summary: str
    evaluation_results: List[Dict[str, Any]]
    identified_gaps: List[str]
    recommendations: List[str]
    limitations: List[str]
    areas_for_human_verification: List[str]
    model_name: Optional[str]
    status: str
    raw_error: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientSubmissionReviewResponse(BaseModel):
    """Client decision audit record."""

    id: uuid.UUID
    submission_id: uuid.UUID
    reviewer_user_id: uuid.UUID
    decision: ClientSubmissionDecision
    comment: Optional[str]
    created_at: datetime
    reviewer: UserResponse

    model_config = ConfigDict(from_attributes=True)


class MilestoneSubmissionResponse(BaseModel):
    """Full milestone submission record with evidence and reviews."""

    id: uuid.UUID
    milestone_id: uuid.UUID
    submitted_by_id: uuid.UUID
    attempt_number: int
    description: str
    notes: Optional[str]
    demonstration_url: Optional[str]
    acceptance_criteria_snapshot: List[str]
    status: SubmissionStatus
    ai_review_status: AIReviewStatus
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    submitted_by: UserResponse
    evidence: List[SubmissionEvidenceResponse] = []
    ai_reviews: List[AISubmissionReviewResponse] = []
    client_reviews: List[ClientSubmissionReviewResponse] = []

    model_config = ConfigDict(from_attributes=True)


class MilestoneSubmissionListResponse(BaseModel):
    """Collection of submission attempts for a milestone."""

    submissions: List[MilestoneSubmissionResponse]
    total: int

