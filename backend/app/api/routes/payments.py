import logging
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.payment import (
    CreatePaymentRequest,
    MockConfirmPaymentRequest,
    PaymentEligibilityResponse,
    PaymentListResponse,
    PaymentResponse,
    PaymentStatusCheckResponse,
)
from app.services.payments import payment_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Milestone Payments & PayPal Checkout"])


# ============================================================================
# PROJECT & MILESTONE SCOPED PAYMENT ROUTES
# ============================================================================

@router.get(
    "/projects/{project_id}/milestones/{milestone_id}/payment-eligibility",
    response_model=PaymentEligibilityResponse,
    summary="Check if approved milestone is eligible for checkout",
    description="Validates project membership, plan agreement, milestone deliverable approval, and existing payment state.",
)
def get_payment_eligibility(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check payment eligibility for an approved milestone."""
    return payment_service.check_payment_eligibility(
        project_id=project_id,
        milestone_id=milestone_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/projects/{project_id}/milestones/{milestone_id}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate payment checkout for an approved milestone",
    description="Creates an internal payment record and calls the configured provider (PayPal Sandbox or Mock) to create an order.",
)
async def create_payment(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    req: Optional[CreatePaymentRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Initiate a payment checkout for an approved milestone."""
    provider_override = req.provider if req else None
    payment = await payment_service.create_milestone_payment(
        project_id=project_id,
        milestone_id=milestone_id,
        current_user=current_user,
        provider_name=provider_override,
        db=db,
    )
    return payment


# ============================================================================
# PAYMENT TRANSACTION LEVEL ROUTES
# ============================================================================

@router.get(
    "/payments",
    response_model=PaymentListResponse,
    summary="List payments history",
    description="Returns payment records accessible to the authenticated client or freelancer, with optional filters.",
)
def list_payments(
    project_id: Optional[uuid.UUID] = Query(None, description="Filter by project ID"),
    milestone_id: Optional[uuid.UUID] = Query(None, description="Filter by milestone ID"),
    status: Optional[str] = Query(None, description="Filter by payment status"),
    provider: Optional[str] = Query(None, description="Filter by provider ('mock' or 'paypal')"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List accessible payments with filtering."""
    payments = payment_service.list_payments(
        current_user=current_user,
        project_id=project_id,
        milestone_id=milestone_id,
        status_filter=status,
        provider_filter=provider,
        db=db,
    )
    return PaymentListResponse(payments=payments, total=len(payments))


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
    summary="Get payment details",
    description="Retrieves a payment transaction record with its complete audit events if the user is an authorized project member.",
)
def get_payment(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve payment record by ID."""
    return payment_service.get_payment_by_id(
        payment_id=payment_id,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/payments/{payment_id}/status",
    response_model=PaymentStatusCheckResponse,
    summary="Get and reconcile real-time payment order status",
    description="Retrieves live PayPal order status, reconciles internal state, and reports whether order is ready for capture.",
)
async def get_payment_lifecycle_status(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve real-time payment reconciliation status."""
    return await payment_service.get_payment_lifecycle_status(
        payment_id=payment_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/payments/{payment_id}/capture",
    response_model=PaymentResponse,
    summary="Capture an approved PayPal or Mock order",
    description="Captures the payment via backend server-to-server call and validates the capture response.",
)
async def capture_payment(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Capture payment order."""
    return await payment_service.capture_milestone_payment(
        payment_id=payment_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/payments/{payment_id}/mock-confirm",
    response_model=PaymentResponse,
    summary="Simulate payment confirmation (Dev/Test only)",
    description="Simulates a buyer completing or cancelling a mock payment. Strictly rejected in production mode.",
)
async def mock_confirm_payment(
    payment_id: uuid.UUID,
    req: MockConfirmPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Simulate client confirming or cancelling a mock payment."""
    return await payment_service.mock_confirm_payment(
        payment_id=payment_id,
        current_user=current_user,
        outcome=req.outcome,
        db=db,
    )


# ============================================================================
# PUBLIC PAYPAL WEBHOOK ROUTE
# ============================================================================

@router.post(
    "/webhooks/paypal",
    status_code=status.HTTP_200_OK,
    summary="PayPal Webhook listener",
    description="Public webhook endpoint called by PayPal. Every incoming event is verified using PayPal signature verification.",
)
async def paypal_webhook_listener(
    request: Request,
    db: Session = Depends(get_db),
):
    """Process incoming PayPal webhooks with signature verification."""
    raw_body = await request.body()
    headers = dict(request.headers)

    result = await payment_service.process_paypal_webhook(
        headers=headers,
        raw_body=raw_body,
        db=db,
    )
    return result
