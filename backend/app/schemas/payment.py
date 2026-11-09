from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    MilestonePaymentStatus,
    PaymentEventSource,
    PaymentProvider,
    PaymentStatus,
)
from app.schemas.auth import UserResponse


class PaymentEligibilityResponse(BaseModel):
    """Eligibility status of an approved milestone for checkout."""

    eligible: bool
    reason: Optional[str] = None
    amount: Decimal
    currency: str
    payment_status: MilestonePaymentStatus
    active_payment_id: Optional[str] = None
    active_provider_order_id: Optional[str] = None
    completed_payment_id: Optional[str] = None
    provider: str


class CreatePaymentRequest(BaseModel):
    """Payload to initiate milestone payment checkout."""

    provider: Optional[str] = Field(
        None,
        description="Optional provider override: 'mock' or 'paypal'. Defaults to backend setting.",
    )


class MockConfirmPaymentRequest(BaseModel):
    """Payload for confirming or cancelling a simulated payment."""

    outcome: str = Field(
        "success",
        description="Desired outcome: 'success', 'fail', or 'cancel'",
    )


class PaymentEventResponse(BaseModel):
    """Immutable audit event for a payment transaction."""

    id: uuid.UUID
    payment_id: uuid.UUID
    event_type: str
    provider_event_id: Optional[str] = None
    event_source: PaymentEventSource
    event_payload: Dict[str, Any]
    processed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentProjectInfo(BaseModel):
    """Minimal project summary for payment representation."""

    id: uuid.UUID
    title: str

    model_config = ConfigDict(from_attributes=True)


class PaymentMilestoneInfo(BaseModel):
    """Minimal milestone summary for payment representation."""

    id: uuid.UUID
    title: str

    model_config = ConfigDict(from_attributes=True)


class PaymentResponse(BaseModel):
    """Payment transaction details."""

    id: uuid.UUID
    milestone_id: uuid.UUID
    project_id: uuid.UUID
    client_user_id: uuid.UUID
    freelancer_user_id: uuid.UUID
    provider: PaymentProvider
    provider_order_id: Optional[str] = None
    provider_capture_id: Optional[str] = None
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_method: Optional[str] = None
    failure_reason: Optional[str] = None
    provider_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    client: Optional[UserResponse] = None
    freelancer: Optional[UserResponse] = None
    project: Optional[PaymentProjectInfo] = None
    milestone: Optional[PaymentMilestoneInfo] = None
    events: List[PaymentEventResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PaymentListResponse(BaseModel):
    """List collection of payments."""

    payments: List[PaymentResponse]
    total: int


class PaymentStatusCheckResponse(BaseModel):
    """Real-time provider reconciliation status response."""

    payment_id: uuid.UUID
    project_id: uuid.UUID
    milestone_id: uuid.UUID
    provider: PaymentProvider
    provider_order_id: Optional[str] = None
    provider_capture_id: Optional[str] = None
    amount: Decimal
    currency: str
    internal_status: PaymentStatus
    stage: str = Field(
        ...,
        description="Checkout stage: buyer_approval_required, buyer_approved, capture_pending, completed, failed, cancelled",
    )
    can_capture: bool
    provider_status: Optional[str] = None
    approval_url: Optional[str] = None
    payer_email: Optional[str] = None
    payer_id: Optional[str] = None
    failure_reason: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
