import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import MilestonePaymentStatus, MilestoneStatus

if TYPE_CHECKING:
    from app.models.milestone_plan import MilestonePlan
    from app.models.milestone_submission import MilestoneSubmission
    from app.models.payment import Payment


class Milestone(Base):
    """Specific deliverable phase within a milestone plan."""

    __tablename__ = "milestones"
    __table_args__ = (
        UniqueConstraint(
            "plan_id",
            "sequence_number",
            name="uq_milestones_plan_sequence",
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
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    deliverables: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    acceptance_criteria: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    estimated_duration_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    budget_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    status: Mapped[MilestoneStatus] = mapped_column(
        Enum(
            MilestoneStatus,
            name="milestonestatus",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=MilestoneStatus.NOT_STARTED,
        nullable=False,
        index=True,
    )
    payment_status: Mapped[MilestonePaymentStatus] = mapped_column(
        Enum(
            MilestonePaymentStatus,
            name="milestonepaymentstatus",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=MilestonePaymentStatus.UNPAID,
        nullable=False,
        index=True,
    )
    dependencies: Mapped[List[int]] = mapped_column(JSONB, default=list, nullable=False)
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
    plan: Mapped["MilestonePlan"] = relationship("MilestonePlan", back_populates="milestones")
    submissions: Mapped[List["MilestoneSubmission"]] = relationship(
        "MilestoneSubmission",
        back_populates="milestone",
        cascade="all, delete-orphan",
        order_by="MilestoneSubmission.attempt_number.desc()",
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="milestone",
        cascade="all, delete-orphan",
        order_by="Payment.created_at.desc()",
    )

