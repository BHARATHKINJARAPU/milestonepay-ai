import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ClientSubmissionDecision

if TYPE_CHECKING:
    from app.models.milestone_submission import MilestoneSubmission
    from app.models.user import User


class AISubmissionReview(Base):
    """AI evaluation audit report assessing evidence against exact agreed acceptance criteria."""

    __tablename__ = "ai_submission_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("milestone_submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    review_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    overall_summary: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_results: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    identified_gaps: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    recommendations: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    limitations: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    areas_for_human_verification: Mapped[List[str]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    raw_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    submission: Mapped["MilestoneSubmission"] = relationship(
        "MilestoneSubmission", back_populates="ai_reviews"
    )


class ClientSubmissionReview(Base):
    """Decision audit record by the project client approving work or requesting revisions."""

    __tablename__ = "client_submission_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("milestone_submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    decision: Mapped[ClientSubmissionDecision] = mapped_column(
        Enum(
            ClientSubmissionDecision,
            name="clientsubmissiondecision",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    submission: Mapped["MilestoneSubmission"] = relationship(
        "MilestoneSubmission", back_populates="client_reviews"
    )
    reviewer: Mapped["User"] = relationship("User")

