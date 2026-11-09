from datetime import datetime, timezone
from decimal import Decimal
import logging
from typing import Any, Dict, Optional

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
from app.services.payments.paypal_orders import paypal_orders_client
from app.services.payments.paypal_webhooks import paypal_webhook_service

logger = logging.getLogger(__name__)


class PayPalPaymentProvider(PaymentProviderBase):
    """Production and Sandbox implementation for PayPal Payments REST API v2."""

    def __init__(self, orders_client=paypal_orders_client, webhook_service=paypal_webhook_service):
        self.orders = orders_client
        self.webhooks = webhook_service

    async def create_order(
        self,
        payment: Payment,
        milestone: Milestone,
        client: User,
        freelancer: User,
    ) -> PaymentOrderResult:
        """Create a PayPal v2 order for an approved milestone."""
        order_data = await self.orders.create_order(
            payment_id=str(payment.id),
            milestone_title=milestone.title,
            sequence_number=milestone.sequence_number,
            amount=payment.amount,
            currency=payment.currency,
            idempotency_key=payment.idempotency_key,
        )

        provider_order_id = order_data["id"]

        # Extract approval link if available in HATEOAS links
        approval_url: Optional[str] = None
        for link in order_data.get("links", []):
            if link.get("rel") == "payer-action" or link.get("rel") == "approve":
                approval_url = link.get("href")
                break

        return PaymentOrderResult(
            provider_order_id=provider_order_id,
            status=PaymentStatus.ORDER_CREATED,
            provider_metadata=order_data,
            approval_url=approval_url,
        )

    async def capture_order(
        self,
        payment: Payment,
        provider_order_id: str,
    ) -> PaymentCaptureResult:
        """Capture an approved PayPal order and validate capture response."""
        status_code, capture_data = await self.orders.capture_order(
            provider_order_id=provider_order_id,
            idempotency_key=payment.idempotency_key,
        )

        # Extract capture details from purchase_units
        purchase_units = capture_data.get("purchase_units", [])
        if not purchase_units:
            raise ValueError(f"PayPal capture response missing purchase_units for order {provider_order_id}")

        payments_block = purchase_units[0].get("payments", {})
        captures = payments_block.get("captures", [])
        if not captures:
            raise ValueError(f"PayPal capture response missing captures for order {provider_order_id}")

        capture = captures[0]
        capture_id = capture.get("id")
        raw_status = capture.get("status", "COMPLETED").upper()
        amount_data = capture.get("amount", {})
        captured_val_str = amount_data.get("value", "0.00")
        captured_currency = amount_data.get("currency_code", payment.currency).upper()

        captured_amount = Decimal(captured_val_str)

        # Currency and amount safety validation
        if captured_currency != payment.currency.upper():
            raise ValueError(
                f"PayPal captured currency mismatch: expected {payment.currency}, received {captured_currency}"
            )

        if captured_amount != payment.amount:
            raise ValueError(
                f"PayPal captured amount mismatch: expected {payment.amount}, received {captured_amount}"
            )

        # Map PayPal capture status
        if raw_status == "COMPLETED":
            final_status = PaymentStatus.COMPLETED
            completed_at = datetime.now(timezone.utc)
            failure_reason = None
        elif raw_status == "PENDING":
            final_status = PaymentStatus.PROCESSING
            completed_at = None
            failure_reason = None
        else:
            final_status = PaymentStatus.FAILED
            completed_at = None
            failure_reason = f"PayPal capture status: {raw_status}"

        return PaymentCaptureResult(
            provider_capture_id=capture_id,
            status=final_status,
            amount=captured_amount,
            currency=captured_currency,
            provider_metadata=capture_data,
            completed_at=completed_at,
            failure_reason=failure_reason,
        )

    async def get_order_details(self, provider_order_id: str) -> Dict[str, Any]:
        """Fetch order details from PayPal."""
        return await self.orders.get_order(provider_order_id)

    async def verify_webhook(
        self,
        headers: Dict[str, str],
        raw_body: bytes,
        parsed_event: Dict[str, Any],
    ) -> WebhookVerificationResult:
        """Verify authenticity of PayPal webhook notification."""
        return await self.webhooks.verify_signature(
            headers=headers,
            raw_body=raw_body,
            parsed_event=parsed_event,
        )
