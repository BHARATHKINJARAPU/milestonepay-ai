import logging
from typing import Any, Dict
import httpx

from app.core.config import settings
from app.services.payments.base import WebhookVerificationResult
from app.services.payments.paypal_auth import paypal_auth_service

logger = logging.getLogger(__name__)


class PayPalWebhookService:
    """Verifies incoming PayPal webhook authenticity using PayPal's verify-webhook-signature REST endpoint."""

    def __init__(self, auth_service=paypal_auth_service):
        self.auth = auth_service

    @property
    def base_url(self) -> str:
        return settings.PAYPAL_API_BASE_URL.rstrip("/")

    @property
    def webhook_id(self) -> str:
        return settings.PAYPAL_WEBHOOK_ID or ""

    async def verify_signature(
        self,
        headers: Dict[str, str],
        raw_body: bytes,
        parsed_event: Dict[str, Any],
    ) -> WebhookVerificationResult:
        """Verify webhook signature via PayPal's official verification API."""
        if not self.webhook_id:
            logger.warning("PAYPAL_WEBHOOK_ID is not configured in environment. Rejecting webhook.")
            return WebhookVerificationResult(
                is_valid=False,
                verification_status="FAILURE",
                reason="PAYPAL_WEBHOOK_ID is not configured in backend settings.",
            )

        # Normalize header keys to lowercase
        norm_headers = {k.lower(): v for k, v in headers.items()}

        auth_algo = norm_headers.get("paypal-auth-algo")
        cert_url = norm_headers.get("paypal-cert-url")
        transmission_id = norm_headers.get("paypal-transmission-id")
        transmission_sig = norm_headers.get("paypal-transmission-sig")
        transmission_time = norm_headers.get("paypal-transmission-time")

        if not all([auth_algo, cert_url, transmission_id, transmission_sig, transmission_time]):
            logger.error("Incoming PayPal webhook missing required transmission headers")
            return WebhookVerificationResult(
                is_valid=False,
                verification_status="FAILURE",
                reason="Missing required PayPal transmission verification headers.",
            )

        verification_url = f"{self.base_url}/v1/notifications/verify-webhook-signature"
        token = await self.auth.get_access_token()

        verification_payload = {
            "auth_algo": auth_algo,
            "cert_url": cert_url,
            "transmission_id": transmission_id,
            "transmission_sig": transmission_sig,
            "transmission_time": transmission_time,
            "webhook_id": self.webhook_id,
            "webhook_event": parsed_event,
        }

        timeout = httpx.Timeout(settings.PAYPAL_REQUEST_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(
                    verification_url,
                    json=verification_payload,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                )
            except httpx.RequestError as exc:
                logger.error("Network error verifying PayPal webhook signature: %s", str(exc))
                return WebhookVerificationResult(
                    is_valid=False,
                    verification_status="ERROR",
                    reason=f"Network error contacting PayPal verification service: {exc}",
                )

        if response.status_code != 200:
            logger.error(
                "PayPal webhook verification request returned status %d: %s",
                response.status_code,
                response.text,
            )
            return WebhookVerificationResult(
                is_valid=False,
                verification_status="FAILURE",
                reason=f"PayPal verification endpoint returned HTTP {response.status_code}",
            )

        data = response.json()
        verification_status = data.get("verification_status", "FAILURE")
        is_valid = verification_status == "SUCCESS"

        if not is_valid:
            logger.warning(
                "PayPal webhook signature validation failed. Status: %s. Event ID: %s",
                verification_status,
                parsed_event.get("id"),
            )
        else:
            logger.info("PayPal webhook signature successfully verified for event %s", parsed_event.get("id"))

        return WebhookVerificationResult(
            is_valid=is_valid,
            verification_status=verification_status,
        )


paypal_webhook_service = PayPalWebhookService()
