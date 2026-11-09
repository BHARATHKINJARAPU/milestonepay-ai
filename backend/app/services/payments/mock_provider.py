from datetime import datetime, timezone
from decimal import Decimal
import logging
from typing import Any, Dict, Optional
import uuid

from app.core.config import settings
from app.models.enums import PaymentStatus
from app.models.milestone import Milestone
from app.models.payment import Payment
from app.models.user import User
from app.services.payments.base import (
    PaymentCaptureResult,
    PaymentOrderResult,
    PaymentProviderBase,
    WebhookVerificationResult,
)

logger = logging.getLogger(__name__)

SIMULATION_NOTICE = "SIMULATED PAYMENT — NOT A REAL PAYPAL TRANSACTION"


class MockPaymentProvider(PaymentProviderBase):
    """Simulated payment provider strictly intended for local development and automated testing."""

    def __init__(self):
        if settings.ENVIRONMENT == "production":
            raise RuntimeError("MockPaymentProvider cannot be initialized in production environment.")

    async def create_order(
        self,
        payment: Payment,
        milestone: Milestone,
        client: User,
        freelancer: User,
    ) -> PaymentOrderResult:
        """Create a simulated order record."""
        order_suffix = uuid.uuid4().hex[:12].upper()
        provider_order_id = f"MOCK-ORD-{order_suffix}"

        metadata = {
            "provider": "mock",
            "is_simulated": True,
            "simulation_notice": SIMULATION_NOTICE,
            "order_id": provider_order_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "milestone_title": milestone.title,
            "client_email": client.email,
            "freelancer_email": freelancer.email,
            "amount": str(payment.amount),
            "currency": payment.currency,
        }

        logger.info(
            "Created MOCK payment order %s for payment %s (Amount: %s %s)",
            provider_order_id,
            payment.id,
            payment.amount,
            payment.currency,
        )

        return PaymentOrderResult(
            provider_order_id=provider_order_id,
            status=PaymentStatus.ORDER_CREATED,
            provider_metadata=metadata,
            approval_url=f"/payments/{payment.id}/mock-checkout",
        )

    async def capture_order(
        self,
        payment: Payment,
        provider_order_id: str,
    ) -> PaymentCaptureResult:
        """Capture the simulated payment order."""
        # Check if the payment metadata requested a simulated failure
        should_fail = payment.provider_metadata.get("simulate_failure", False)
        if should_fail:
            return PaymentCaptureResult(
                provider_capture_id=f"MOCK-FAIL-{uuid.uuid4().hex[:8].upper()}",
                status=PaymentStatus.FAILED,
                amount=payment.amount,
                currency=payment.currency,
                provider_metadata={
                    "provider": "mock",
                    "is_simulated": True,
                    "simulation_notice": SIMULATION_NOTICE,
                    "failure_reason": "Simulated payment failure requested by client test.",
                },
                completed_at=None,
                failure_reason="Simulated payment failure requested by client test.",
            )

        capture_suffix = uuid.uuid4().hex[:12].upper()
        provider_capture_id = f"MOCK-CAP-{capture_suffix}"
        now = datetime.now(timezone.utc)

        metadata = {
            "provider": "mock",
            "is_simulated": True,
            "simulation_notice": SIMULATION_NOTICE,
            "order_id": provider_order_id,
            "capture_id": provider_capture_id,
            "status": "COMPLETED",
            "captured_at": now.isoformat(),
            "amount": str(payment.amount),
            "currency": payment.currency,
        }

        logger.info(
            "Captured MOCK payment %s with capture_id %s (Amount: %s %s)",
            payment.id,
            provider_capture_id,
            payment.amount,
            payment.currency,
        )

        return PaymentCaptureResult(
            provider_capture_id=provider_capture_id,
            status=PaymentStatus.COMPLETED,
            amount=payment.amount,
            currency=payment.currency,
            provider_metadata=metadata,
            completed_at=now,
        )

    async def get_order_details(self, provider_order_id: str) -> Dict[str, Any]:
        """Retrieve simulated order status details."""
        return {
            "id": provider_order_id,
            "status": "APPROVED",
            "intent": "CAPTURE",
            "is_simulated": True,
            "simulation_notice": SIMULATION_NOTICE,
        }

    async def verify_webhook(
        self,
        headers: Dict[str, str],
        raw_body: bytes,
        parsed_event: Dict[str, Any],
    ) -> WebhookVerificationResult:
        """Verify simulated webhook authenticity."""
        # For mock provider, verify that event_source or simulated header is present
        mock_token = headers.get("x-mock-webhook-secret", "")
        if mock_token == "invalid-signature":
            return WebhookVerificationResult(
                is_valid=False,
                verification_status="FAILURE",
                reason="Simulated invalid webhook signature header.",
            )

        return WebhookVerificationResult(
            is_valid=True,
            verification_status="SUCCESS",
        )
