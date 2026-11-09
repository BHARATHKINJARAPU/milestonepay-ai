import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import AIReviewStatus, SubmissionStatus

if TYPE_CHECKING:
    from app.models.milestone import Milestone
    from app.models.submission_evidence import SubmissionEvidence
    from app.models.submission_review import AISubmissionReview, ClientSubmissionReview
    from app.models.user import User


class MilestoneSubmission(Base):
    """An attempt by a freelancer to submit deliverables for milestone completion."""

    __tablename__ = "milestone_submissions"
    __table_args__ = (
        UniqueConstraint(
            "milestone_id",
            "attempt_number",
            name="uq_milestone_submissions_milestone_attempt",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    milestone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("milestones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submitted_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    demonstration_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    acceptance_criteria_snapshot: Mapped[List[str]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(
            SubmissionStatus,
            name="submissionstatus",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=SubmissionStatus.DRAFT,
        nullable=False,
        index=True,
    )
    ai_review_status: Mapped[AIReviewStatus] = mapped_column(
        Enum(
            AIReviewStatus,
            name="aireviewstatus",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=AIReviewStatus.PENDING,
        nullable=False,
        index=True,
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="submissions")
    submitted_by: Mapped["User"] = relationship("User")
    evidence: Mapped[List["SubmissionEvidence"]] = relationship(
        "SubmissionEvidence",
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionEvidence.created_at.asc()",
    )
    ai_reviews: Mapped[List["AISubmissionReview"]] = relationship(
        "AISubmissionReview",
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="AISubmissionReview.review_version.desc()",
    )
    client_reviews: Mapped[List["ClientSubmissionReview"]] = relationship(
        "ClientSubmissionReview",
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="ClientSubmissionReview.created_at.desc()",
    )

