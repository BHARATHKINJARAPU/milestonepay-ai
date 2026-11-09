import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import PlanGenerationSource, PlanStatus

if TYPE_CHECKING:
    from app.models.milestone import Milestone
    from app.models.milestone_plan_review import MilestonePlanReview
    from app.models.project import Project
    from app.models.user import User


class MilestonePlan(Base):
    """Milestone agreement plan representing an AI-generated or manually authored proposal version."""

    __tablename__ = "milestone_plans"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "version",
            name="uq_milestone_plans_project_version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[PlanStatus] = mapped_column(
        SAEnum(PlanStatus, name="plan_status_enum", native_enum=False),
        default=PlanStatus.DRAFT,
        nullable=False,
        index=True,
    )
    project_summary: Mapped[str] = mapped_column(Text, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    assumptions: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    clarifying_questions: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    risks: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    needs_clarification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    generation_source: Mapped[PlanGenerationSource] = mapped_column(
        SAEnum(PlanGenerationSource, name="plan_generation_source_enum", native_enum=False),
        default=PlanGenerationSource.AI,
        nullable=False,
    )
    ai_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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
    project: Mapped["Project"] = relationship("Project", back_populates="milestone_plans")
    creator: Mapped["User"] = relationship("User")
    milestones: Mapped[List["Milestone"]] = relationship(
        "Milestone",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="Milestone.sequence_number",
    )
    reviews: Mapped[List["MilestonePlanReview"]] = relationship(
        "MilestonePlanReview",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="MilestonePlanReview.created_at.desc()",
    )

