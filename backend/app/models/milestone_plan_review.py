import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import MemberRole, ReviewDecision

if TYPE_CHECKING:
    from app.models.milestone_plan import MilestonePlan
    from app.models.user import User


class MilestonePlanReview(Base):
    """Review decision (approval or changes requested) submitted by a project member for a plan version."""

    __tablename__ = "milestone_plan_reviews"
    __table_args__ = (
        UniqueConstraint(
            "plan_id",
            "reviewer_user_id",
            name="uq_plan_reviews_plan_reviewer",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("milestone_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_role: Mapped[MemberRole] = mapped_column(
        SAEnum(MemberRole, name="member_role_enum", native_enum=False),
        nullable=False,
    )
    decision: Mapped[ReviewDecision] = mapped_column(
        SAEnum(ReviewDecision, name="review_decision_enum", native_enum=False),
        nullable=False,
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    plan: Mapped["MilestonePlan"] = relationship("MilestonePlan", back_populates="reviews")
    reviewer: Mapped["User"] = relationship("User")

