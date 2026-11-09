from datetime import datetime, timezone
from decimal import Decimal
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.enums import (
    MemberRole,
    MilestonePaymentStatus,
    MilestoneStatus,
    PaymentEventSource,
    PaymentProvider,
    PaymentStatus,
    PlanStatus,
    WebhookProcessingStatus,
)
from app.models.milestone import Milestone
from app.models.milestone_plan import MilestonePlan
from app.models.payment import Payment, PaymentEvent, PayPalWebhookEvent
from app.models.project import Project
from app.models.user import User
from app.services.activity_service import activity_service
from app.services.notification_service import notification_service
from app.services.payments.base import PaymentProviderBase
from app.services.payments.mock_provider import MockPaymentProvider
from app.services.payments.paypal_orders import paypal_orders_client
from app.services.payments.paypal_provider import PayPalPaymentProvider

logger = logging.getLogger(__name__)


class PaymentService:
    """Coordinates milestone payment workflows across configured providers."""

    def __init__(self):
        self._mock_provider = MockPaymentProvider() if settings.ENVIRONMENT != "production" else None
        self._paypal_provider = PayPalPaymentProvider()

    def get_provider(self, provider_name: Optional[str] = None) -> PaymentProviderBase:
        """Return the requested or configured payment provider."""
        target = (provider_name or settings.PAYMENT_PROVIDER).strip().lower()

        if target == PaymentProvider.MOCK.value:
            if settings.ENVIRONMENT == "production":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mock payment provider is strictly prohibited in production mode.",
                )
            if not self._mock_provider:
                self._mock_provider = MockPaymentProvider()
            return self._mock_provider

        elif target == PaymentProvider.PAYPAL.value:
            return self._paypal_provider

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported payment provider '{target}'. Allowed options: 'mock', 'paypal'.",
        )

    def check_payment_eligibility(
        self,
        project_id: uuid.UUID,
        milestone_id: uuid.UUID,
        current_user: User,
        db: Session,
    ) -> Dict[str, Any]:
        """Verify whether an authenticated user is eligible to initiate milestone payment."""
        milestone = (
            db.query(Milestone)
            .options(
                joinedload(Milestone.plan).joinedload(MilestonePlan.project).joinedload(Project.members)
            )
            .filter(Milestone.id == milestone_id)
            .first()
        )

        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone could not be found.",
            )

        project = milestone.plan.project
        if project.id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Milestone does not belong to the specified project.",
            )

        # 1. Project client membership verification
        membership = next((m for m in project.members if m.user_id == current_user.id), None)
        if not membership or membership.role != MemberRole.CLIENT:
            return {
                "eligible": False,
                "reason": "Only the assigned client of this project can initiate milestone payments.",
                "amount": milestone.amount,
                "currency": milestone.currency,
                "payment_status": milestone.payment_status.value,
                "provider": settings.PAYMENT_PROVIDER,
            }

        # 2. Plan agreement verification
        if milestone.plan.status != PlanStatus.AGREED:
            return {
                "eligible": False,
                "reason": f"Milestone plan is in '{milestone.plan.status.value}' state. Both client and freelancer must agree to the plan before payments can be processed.",
                "amount": milestone.amount,
                "currency": milestone.currency,
                "payment_status": milestone.payment_status.value,
                "provider": settings.PAYMENT_PROVIDER,
            }

        # 3. Deliverable approval verification
        if milestone.status != MilestoneStatus.APPROVED:
            return {
                "eligible": False,
                "reason": f"Milestone deliverables have not been approved yet (current status: '{milestone.status.value}'). Payment can only be released after explicit client approval.",
                "amount": milestone.amount,
                "currency": milestone.currency,
                "payment_status": milestone.payment_status.value,
                "provider": settings.PAYMENT_PROVIDER,
            }

        # 4. Amount validation
        if milestone.amount <= Decimal("0.00"):
            return {
                "eligible": False,
                "reason": "Milestone amount must be greater than zero.",
                "amount": milestone.amount,
                "currency": milestone.currency,
                "payment_status": milestone.payment_status.value,
                "provider": settings.PAYMENT_PROVIDER,
            }

        # 5. Completed payment check
        existing_completed = (
            db.query(Payment)
            .filter(
                Payment.milestone_id == milestone.id,
                Payment.status == PaymentStatus.COMPLETED,
            )
            .first()
        )
        if existing_completed:
            return {
                "eligible": False,
                "reason": "This milestone has already been paid in full.",
                "amount": milestone.amount,
                "currency": milestone.currency,
                "payment_status": MilestonePaymentStatus.COMPLETED.value,
                "completed_payment_id": str(existing_completed.id),
                "provider": settings.PAYMENT_PROVIDER,
            }

        # 6. Active payment in-progress check
        existing_active = (
            db.query(Payment)
            .filter(
                Payment.milestone_id == milestone.id,
                Payment.status.in_([
                    PaymentStatus.ORDER_CREATED,
                    PaymentStatus.PAYER_APPROVED,
                    PaymentStatus.PROCESSING,
                ]),
            )
            .order_by(Payment.created_at.desc())
            .first()
        )

        return {
            "eligible": True,
            "reason": None,
            "amount": milestone.amount,
            "currency": milestone.currency,
            "payment_status": milestone.payment_status.value,
            "active_payment_id": str(existing_active.id) if existing_active else None,
            "active_provider_order_id": existing_active.provider_order_id if existing_active else None,
            "provider": settings.PAYMENT_PROVIDER,
        }

    async def create_milestone_payment(
        self,
        project_id: uuid.UUID,
        milestone_id: uuid.UUID,
        current_user: User,
        provider_name: Optional[str],
        db: Session,
    ) -> Payment:
        """Initiate payment for an approved milestone using the active payment provider."""
        eligibility = self.check_payment_eligibility(
            project_id=project_id,
            milestone_id=milestone_id,
            current_user=current_user,
            db=db,
        )

        if not eligibility["eligible"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=eligibility["reason"],
            )

        milestone = (
            db.query(Milestone)
            .options(
                joinedload(Milestone.plan).joinedload(MilestonePlan.project).joinedload(Project.members)
            )
            .filter(Milestone.id == milestone_id)
            .first()
        )

        project = milestone.plan.project
        freelancer_member = next((m for m in project.members if m.role == MemberRole.FREELANCER), None)
        if not freelancer_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project does not have an assigned freelancer to receive milestone attribution.",
            )

        selected_provider_type = (provider_name or settings.PAYMENT_PROVIDER).strip().lower()
        provider_enum = (
            PaymentProvider.MOCK
            if selected_provider_type == PaymentProvider.MOCK.value
            else PaymentProvider.PAYPAL
        )

        provider_instance = self.get_provider(selected_provider_type)

        # Idempotency key for this payment creation
        idempotency_key = f"pay-{milestone.id}-{uuid.uuid4().hex[:12]}"

        # 1. Create internal Payment in PENDING status
        payment = Payment(
            milestone_id=milestone.id,
            project_id=project.id,
            client_user_id=current_user.id,
            freelancer_user_id=freelancer_member.user_id,
            provider=provider_enum,
            amount=milestone.amount,
            currency=milestone.currency,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
            provider_metadata={
                "provider": selected_provider_type,
                "project_title": project.title,
                "milestone_title": milestone.title,
            },
        )
        db.add(payment)
        db.flush()

        # 2. Record initial payment event
        init_event = PaymentEvent(
            payment_id=payment.id,
            event_type="PAYMENT_INITIALIZED",
            event_source=PaymentEventSource.MOCK if provider_enum == PaymentProvider.MOCK else PaymentEventSource.PAYPAL_API,
            event_payload={
                "amount": str(payment.amount),
                "currency": payment.currency,
                "provider": provider_enum.value,
            },
            processed=True,
        )
        db.add(init_event)
        db.commit()

        # 3. Call provider to create upstream order
        try:
            freelancer_user = db.query(User).filter(User.id == freelancer_member.user_id).first()
            order_result = await provider_instance.create_order(
                payment=payment,
                milestone=milestone,
                client=current_user,
                freelancer=freelancer_user,
            )
        except Exception as exc:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = str(exc)
            db.commit()
            logger.error("Failed to create provider order for payment %s: %s", payment.id, str(exc))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment provider error: {str(exc)}",
            )

        # 4. Update payment with provider order ID and transition milestone to PENDING
        payment.provider_order_id = order_result.provider_order_id
        payment.status = order_result.status
        payment.provider_metadata = {**payment.provider_metadata, **order_result.provider_metadata}
        milestone.payment_status = MilestonePaymentStatus.PENDING

        order_event = PaymentEvent(
            payment_id=payment.id,
            event_type="ORDER_CREATED",
            provider_event_id=order_result.provider_order_id,
            event_source=PaymentEventSource.MOCK if provider_enum == PaymentProvider.MOCK else PaymentEventSource.PAYPAL_API,
            event_payload={
                "provider_order_id": order_result.provider_order_id,
                "status": order_result.status.value,
                "approval_url": order_result.approval_url,
            },
            processed=True,
        )
        db.add(order_event)
        db.commit()

        logger.info("Payment %s created with provider order %s (status: %s)", payment.id, payment.provider_order_id, payment.status.value)
        return payment

    async def get_payment_lifecycle_status(
        self,
        payment_id: uuid.UUID,
        current_user: User,
        db: Session,
    ) -> Dict[str, Any]:
        """Inspect and reconcile real-time payment order status across internal DB and PayPal."""
        payment = (
            db.query(Payment)
            .options(
                joinedload(Payment.milestone),
                joinedload(Payment.project).joinedload(Project.members),
            )
            .filter(Payment.id == payment_id)
            .first()
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record could not be found.",
            )

        # Verify project membership (client or freelancer)
        member_ids = [m.user_id for m in payment.project.members]
        if current_user.id not in member_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this payment transaction.",
            )

        # Extract approval link from provider metadata
        links = payment.provider_metadata.get("links", [])
        approval_url = next(
            (l.get("href") for l in links if l.get("rel") in ("approve", "payer-action")),
            None,
        )

        stage = "buyer_approval_required"
        can_capture = False
        provider_status = None
        payer_email = None
        payer_id = None

        if payment.status == PaymentStatus.COMPLETED:
            stage = "completed"
            can_capture = False
            provider_status = "COMPLETED"
        elif payment.status == PaymentStatus.CANCELLED:
            stage = "cancelled"
            can_capture = False
            provider_status = "CANCELLED"
        elif payment.status == PaymentStatus.FAILED:
            stage = "failed"
            can_capture = False
            provider_status = "FAILED"
        elif payment.provider == PaymentProvider.MOCK:
            if payment.status == PaymentStatus.PAYER_APPROVED:
                stage = "buyer_approved"
                can_capture = True
                provider_status = "APPROVED"
            else:
                stage = "buyer_approval_required"
                can_capture = False
                provider_status = "CREATED"
        elif payment.provider == PaymentProvider.PAYPAL:
            if not payment.provider_order_id:
                stage = "failed"
                can_capture = False
            else:
                try:
                    order_data = await paypal_orders_client.get_order(payment.provider_order_id)
                    provider_status = order_data.get("status", "CREATED")

                    # Extract approval link if available in fresh order data
                    fresh_links = order_data.get("links", [])
                    fresh_appr = next(
                        (l.get("href") for l in fresh_links if l.get("rel") in ("approve", "payer-action")),
                        None,
                    )
                    if fresh_appr:
                        approval_url = fresh_appr

                    payer = order_data.get("payer", {})
                    payer_email = payer.get("email_address")
                    payer_id = payer.get("payer_id")

                    if provider_status == "CREATED":
                        stage = "buyer_approval_required"
                        can_capture = False
                        if payment.status != PaymentStatus.ORDER_CREATED:
                            payment.status = PaymentStatus.ORDER_CREATED
                            db.commit()

                    elif provider_status == "APPROVED":
                        stage = "buyer_approved"
                        can_capture = True
                        if payment.status != PaymentStatus.PAYER_APPROVED:
                            payment.status = PaymentStatus.PAYER_APPROVED
                            payment.provider_metadata = {
                                **payment.provider_metadata,
                                "payer": payer,
                                "paypal_status": "APPROVED",
                            }
                            # Log audit event
                            approved_event_id = f"{payment.provider_order_id}-APPROVED"
                            existing_approved_event = (
                                db.query(PaymentEvent)
                                .filter(
                                    PaymentEvent.payment_id == payment.id,
                                    PaymentEvent.event_type == "PAYER_APPROVED",
                                )
                                .first()
                            )
                            if not existing_approved_event:
                                db.add(
                                    PaymentEvent(
                                        payment_id=payment.id,
                                        event_type="PAYER_APPROVED",
                                        provider_event_id=approved_event_id,
                                        event_source=PaymentEventSource.PAYPAL_API,
                                        event_payload={"order_id": payment.provider_order_id, "payer": payer},
                                        processed=True,
                                    )
                                )
                            db.commit()

                    elif provider_status == "COMPLETED":
                        stage = "completed"
                        can_capture = False
                        if payment.status != PaymentStatus.COMPLETED:
                            payment.status = PaymentStatus.COMPLETED
                            payment.milestone.payment_status = MilestonePaymentStatus.COMPLETED
                            db.commit()

                    elif provider_status in ("VOIDED", "EXPIRED"):
                        stage = "cancelled"
                        can_capture = False
                        payment.status = PaymentStatus.CANCELLED
                        db.commit()

                except Exception as exc:
                    logger.warning("Failed to refresh live PayPal order status for %s: %s", payment.provider_order_id, str(exc))
                    provider_status = "UNAVAILABLE"
                    if payment.status == PaymentStatus.PAYER_APPROVED:
                        stage = "buyer_approved"
                        can_capture = True
                    else:
                        stage = "buyer_approval_required"
                        can_capture = False

        return {
            "payment_id": payment.id,
            "project_id": payment.project_id,
            "milestone_id": payment.milestone_id,
            "provider": payment.provider,
            "provider_order_id": payment.provider_order_id,
            "provider_capture_id": payment.provider_capture_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "internal_status": payment.status,
            "stage": stage,
            "can_capture": can_capture,
            "provider_status": provider_status,
            "approval_url": approval_url,
            "payer_email": payer_email,
            "payer_id": payer_id,
            "failure_reason": payment.failure_reason,
            "updated_at": payment.updated_at,
        }

    async def capture_milestone_payment(
        self,
        payment_id: uuid.UUID,
        current_user: User,
        db: Session,
    ) -> Payment:
        """Capture an approved payment order through the backend."""
        payment = (
            db.query(Payment)
            .options(
                joinedload(Payment.milestone),
                joinedload(Payment.project).joinedload(Project.members),
            )
            .filter(Payment.id == payment_id)
            .first()
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record could not be found.",
            )

        # Authorization: only the assigned client can trigger capture
        if payment.client_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the client who initiated this payment can authorize order capture.",
            )

        # Idempotent return if already completed
        if payment.status == PaymentStatus.COMPLETED:
            logger.info("Payment %s was already completed. Returning existing capture record.", payment.id)
            return payment

        if not payment.provider_order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment record does not have an associated provider order ID.",
            )

        provider_instance = self.get_provider(payment.provider.value)

        # Pre-capture verification for PayPal payments
        if payment.provider == PaymentProvider.PAYPAL:
            try:
                order_data = await paypal_orders_client.get_order(payment.provider_order_id)
            except Exception as exc:
                logger.error("Failed to query live PayPal order before capture: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Unable to reach PayPal API to verify order approval: {exc}",
                )

            pp_order_id = order_data.get("id")
            if pp_order_id != payment.provider_order_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PayPal order ID mismatch: expected {payment.provider_order_id}, received {pp_order_id}",
                )

            live_status = order_data.get("status")
            if live_status == "COMPLETED":
                logger.info("PayPal order %s was already completed. Reconciling record.", payment.provider_order_id)
                payment.status = PaymentStatus.COMPLETED
                payment.milestone.payment_status = MilestonePaymentStatus.COMPLETED
                db.commit()
                return payment

            if live_status == "CREATED":
                payment.status = PaymentStatus.ORDER_CREATED
                payment.failure_reason = "Order is awaiting buyer approval in PayPal Sandbox."
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PayPal order has not yet been approved by the buyer. Please complete approval in the PayPal Sandbox window first, then retry capture.",
                )

            if live_status != "APPROVED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PayPal order cannot be captured in status '{live_status}'. Order must be APPROVED by buyer first.",
                )

            # Validate purchase units amount and currency
            purchase_units = order_data.get("purchase_units", [{}])
            if purchase_units:
                amt_block = purchase_units[0].get("amount", {})
                live_val = Decimal(amt_block.get("value", "0.00"))
                live_curr = amt_block.get("currency_code", "").upper()
                if live_val != payment.amount or live_curr != payment.currency.upper():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"PayPal order amount mismatch: expected {payment.currency} {payment.amount}, received {live_curr} {live_val}",
                    )

            # Validated as APPROVED -> update status
            payment.status = PaymentStatus.PAYER_APPROVED
            db.commit()

        # Mark payment as processing
        payment.status = PaymentStatus.PROCESSING
        db.commit()

        try:
            capture_result = await provider_instance.capture_order(
                payment=payment,
                provider_order_id=payment.provider_order_id,
            )
        except Exception as exc:
            err_msg = str(exc)
            if "ORDER_NOT_APPROVED" in err_msg:
                payment.status = PaymentStatus.ORDER_CREATED
                payment.failure_reason = "Order is awaiting buyer approval in PayPal Sandbox."
                db.commit()
                logger.warning("Order %s pending buyer approval in PayPal Sandbox: %s", payment.provider_order_id, err_msg)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PayPal order has not yet been approved by the buyer. Please complete approval in the PayPal Sandbox window first, then retry capture.",
                )
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = err_msg
            db.commit()
            logger.error("Capture failed for payment %s (order %s): %s", payment.id, payment.provider_order_id, err_msg)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment capture error: {err_msg}",
            )

        # Update payment record with verified capture details
        payment.provider_capture_id = capture_result.provider_capture_id
        payment.status = capture_result.status
        payment.completed_at = capture_result.completed_at
        payment.failure_reason = capture_result.failure_reason
        payment.provider_metadata = {**payment.provider_metadata, **capture_result.provider_metadata}

        # Synchronize milestone payment status
        if capture_result.status == PaymentStatus.COMPLETED:
            payment.milestone.payment_status = MilestonePaymentStatus.COMPLETED

            # Record payment captured activity and dispatch notifications
            try:
                activity_service.record_activity(
                    db=db,
                    project_id=payment.project_id,
                    activity_type="payment_captured",
                    title=f"Payment Settled for '{payment.milestone.title}'",
                    actor_user_id=current_user.id,
                    description=f"Payment of {payment.currency} {float(payment.amount):,.2f} captured via {payment.provider.value}. Milestone funds settled.",
                    metadata={"provider": payment.provider.value, "amount": float(payment.amount), "currency": payment.currency},
                )
                notification_service.create_notification(
                    db=db,
                    user_id=payment.freelancer_user_id,
                    notification_type="payment_captured",
                    title="Milestone Payment Released!",
                    message=f"Payment of {payment.currency} {float(payment.amount):,.2f} for '{payment.milestone.title}' has been released by client.",
                    action_url=f"/payments/{payment.id}/result",
                    project_id=payment.project_id,
                    milestone_id=payment.milestone_id,
                )
                notification_service.create_notification(
                    db=db,
                    user_id=payment.client_user_id,
                    notification_type="payment_captured",
                    title="Payment Confirmed",
                    message=f"Your payment of {payment.currency} {float(payment.amount):,.2f} for '{payment.milestone.title}' was successfully captured.",
                    action_url=f"/payments/{payment.id}/result",
                    project_id=payment.project_id,
                    milestone_id=payment.milestone_id,
                )
            except Exception as exc:
                logger.warning("Could not record payment capture activity/notification: %s", exc)

        capture_event = PaymentEvent(
            payment_id=payment.id,
            event_type="CAPTURE_COMPLETED" if capture_result.status == PaymentStatus.COMPLETED else "CAPTURE_FAILED",
            provider_event_id=capture_result.provider_capture_id,
            event_source=PaymentEventSource.MOCK if payment.provider == PaymentProvider.MOCK else PaymentEventSource.PAYPAL_API,
            event_payload={
                "provider_capture_id": capture_result.provider_capture_id,
                "status": capture_result.status.value,
                "amount": str(capture_result.amount),
                "currency": capture_result.currency,
            },
            processed=True,
        )
        db.add(capture_event)
        db.commit()

        logger.info("Payment %s capture finished with status %s", payment.id, payment.status.value)
        return payment

    async def mock_confirm_payment(
        self,
        payment_id: uuid.UUID,
        current_user: User,
        outcome: str,
        db: Session,
    ) -> Payment:
        """Simulate a client confirming or cancelling a mock payment."""
        if settings.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Mock payment confirmation is disabled in production.",
            )

        payment = (
            db.query(Payment)
            .options(joinedload(Payment.milestone))
            .filter(Payment.id == payment_id)
            .first()
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record not found.",
            )

        if payment.provider != PaymentProvider.MOCK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mock confirmation is only valid for simulated payments.",
            )

        if payment.client_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the client who created this payment can confirm it.",
            )

        if outcome == "cancel":
            payment.status = PaymentStatus.CANCELLED
            payment.failure_reason = "Payment cancelled by user."
            payment.milestone.payment_status = MilestonePaymentStatus.UNPAID
            db.commit()
            return payment

        elif outcome == "fail":
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = "Simulated payment failure."
            payment.milestone.payment_status = MilestonePaymentStatus.UNPAID
            db.commit()
            return payment

        # Standard successful capture
        return await self.capture_milestone_payment(payment_id, current_user, db)

    async def process_paypal_webhook(
        self,
        headers: Dict[str, str],
        raw_body: bytes,
        db: Session,
    ) -> Dict[str, Any]:
        """Verify and process an incoming PayPal webhook notification."""
        try:
            parsed_event = json.loads(raw_body.decode("utf-8"))
        except Exception as exc:
            logger.error("Malformed JSON in PayPal webhook: %s", str(exc))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed JSON payload.")

        event_id = parsed_event.get("id")
        event_type = parsed_event.get("event_type", "UNKNOWN")

        if not event_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Webhook payload missing event id.")

        # Check for duplicate event (idempotency)
        existing_event = (
            db.query(PayPalWebhookEvent)
            .filter(PayPalWebhookEvent.paypal_event_id == event_id)
            .first()
        )
        if existing_event and existing_event.processing_status == WebhookProcessingStatus.PROCESSED:
            logger.info("PayPal webhook %s already processed. Acknowledging idempotently.", event_id)
            return {"status": "already_processed", "event_id": event_id}

        # Verify signature with PayPal
        provider = self.get_provider("paypal")
        verification = await provider.verify_webhook(headers, raw_body, parsed_event)

        # Record webhook event in database
        webhook_record = existing_event or PayPalWebhookEvent(
            paypal_event_id=event_id,
            event_type=event_type,
            signature_verified=verification.is_valid,
            processing_status=WebhookProcessingStatus.VERIFIED if verification.is_valid else WebhookProcessingStatus.FAILED,
            event_payload=parsed_event,
        )
        if not existing_event:
            db.add(webhook_record)
        db.commit()

        if not verification.is_valid:
            logger.warning("Rejected unverified PayPal webhook %s (Status: %s)", event_id, verification.verification_status)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhook signature verification failed: {verification.reason}",
            )

        # Match event with internal payment record
        resource = parsed_event.get("resource", {})
        custom_id = resource.get("custom_id")
        order_id = resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id") or resource.get("id")

        matched_payment: Optional[Payment] = None
        if custom_id:
            try:
                matched_payment = db.query(Payment).filter(Payment.id == uuid.UUID(custom_id)).first()
            except Exception:
                pass

        if not matched_payment and order_id:
            matched_payment = (
                db.query(Payment)
                .filter(Payment.provider_order_id == order_id)
                .first()
            )

        if not matched_payment:
            logger.warning("PayPal webhook %s could not be matched to an internal payment record (Order: %s, Custom: %s)", event_id, order_id, custom_id)
            webhook_record.processing_status = WebhookProcessingStatus.PROCESSED
            webhook_record.processed_at = datetime.now(timezone.utc)
            db.commit()
            return {"status": "unmatched_event_recorded", "event_id": event_id}

        # Process specific event types
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            matched_payment.status = PaymentStatus.COMPLETED
            matched_payment.completed_at = datetime.now(timezone.utc)
            matched_payment.provider_capture_id = resource.get("id")
            matched_payment.milestone.payment_status = MilestonePaymentStatus.COMPLETED

            db.add(PaymentEvent(
                payment_id=matched_payment.id,
                event_type="PAYMENT.CAPTURE.COMPLETED",
                provider_event_id=event_id,
                event_source=PaymentEventSource.PAYPAL_WEBHOOK,
                event_payload=resource,
                processed=True,
            ))

        elif event_type == "PAYMENT.CAPTURE.DENIED":
            matched_payment.status = PaymentStatus.FAILED
            matched_payment.failure_reason = "PayPal payment capture denied."

            db.add(PaymentEvent(
                payment_id=matched_payment.id,
                event_type="PAYMENT.CAPTURE.DENIED",
                provider_event_id=event_id,
                event_source=PaymentEventSource.PAYPAL_WEBHOOK,
                event_payload=resource,
                processed=True,
            ))

        elif event_type == "CHECKOUT.ORDER.APPROVED":
            matched_payment.status = PaymentStatus.PAYER_APPROVED

            db.add(PaymentEvent(
                payment_id=matched_payment.id,
                event_type="CHECKOUT.ORDER.APPROVED",
                provider_event_id=event_id,
                event_source=PaymentEventSource.PAYPAL_WEBHOOK,
                event_payload=resource,
                processed=True,
            ))

        webhook_record.processing_status = WebhookProcessingStatus.PROCESSED
        webhook_record.processed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info("Successfully processed PayPal webhook %s for payment %s", event_id, matched_payment.id)
        return {"status": "processed", "event_id": event_id, "payment_id": str(matched_payment.id)}

    def get_payment_by_id(
        self,
        payment_id: uuid.UUID,
        current_user: User,
        db: Session,
    ) -> Payment:
        """Retrieve payment details if current user is an authorized project member."""
        payment = (
            db.query(Payment)
            .options(
                joinedload(Payment.milestone),
                joinedload(Payment.project).joinedload(Project.members),
                joinedload(Payment.client),
                joinedload(Payment.freelancer),
                joinedload(Payment.events),
            )
            .filter(Payment.id == payment_id)
            .first()
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record could not be found.",
            )

        is_member = any(m.user_id == current_user.id for m in payment.project.members)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this payment.",
            )

        return payment

    def list_payments(
        self,
        current_user: User,
        project_id: Optional[uuid.UUID],
        milestone_id: Optional[uuid.UUID],
        status_filter: Optional[str],
        provider_filter: Optional[str],
        db: Session,
    ) -> List[Payment]:
        """List payments accessible to the current user with optional filters."""
        query = (
            db.query(Payment)
            .options(
                joinedload(Payment.milestone),
                joinedload(Payment.project),
                joinedload(Payment.client),
                joinedload(Payment.freelancer),
            )
            .join(Project, Payment.project_id == Project.id)
        )

        # Restrict to projects where user is client or freelancer
        query = query.filter(
            (Payment.client_user_id == current_user.id) | (Payment.freelancer_user_id == current_user.id)
        )

        if project_id:
            query = query.filter(Payment.project_id == project_id)
        if milestone_id:
            query = query.filter(Payment.milestone_id == milestone_id)
        if status_filter:
            try:
                query = query.filter(Payment.status == PaymentStatus(status_filter.lower()))
            except ValueError:
                pass
        if provider_filter:
            try:
                query = query.filter(Payment.provider == PaymentProvider(provider_filter.lower()))
            except ValueError:
                pass

        return query.order_by(Payment.created_at.desc()).all()


payment_service = PaymentService()
