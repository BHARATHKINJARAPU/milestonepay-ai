from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from app.models.enums import PaymentStatus
from app.models.milestone import Milestone
from app.models.payment import Payment
from app.models.user import User


@dataclass
class PaymentOrderResult:
    """Output from creating an upstream order with a payment provider."""

    provider_order_id: str
    status: PaymentStatus
    provider_metadata: Dict[str, Any]
    approval_url: Optional[str] = None


@dataclass
class PaymentCaptureResult:
    """Output from capturing/confirming payment with an upstream provider."""

    provider_capture_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    provider_metadata: Dict[str, Any]
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None


@dataclass
class WebhookVerificationResult:
    """Cryptographic or API verification result for an incoming provider webhook."""

    is_valid: bool
    verification_status: str
    reason: Optional[str] = None


class PaymentProviderBase(ABC):
    """Abstract interface defining required provider operations."""

    @abstractmethod
    async def create_order(
        self,
        payment: Payment,
        milestone: Milestone,
        client: User,
        freelancer: User,
    ) -> PaymentOrderResult:
        """Create an order with the payment provider."""
        pass

    @abstractmethod
    async def capture_order(
        self,
        payment: Payment,
        provider_order_id: str,
    ) -> PaymentCaptureResult:
        """Capture funds for an approved payment order."""
        pass

    @abstractmethod
    async def get_order_details(
        self,
        provider_order_id: str,
    ) -> Dict[str, Any]:
        """Retrieve latest order details from the provider for reconciliation."""
        pass

    @abstractmethod
    async def verify_webhook(
        self,
        headers: Dict[str, str],
        raw_body: bytes,
        parsed_event: Dict[str, Any],
    ) -> WebhookVerificationResult:
        """Verify authenticity of an incoming webhook event."""
        pass
