from decimal import Decimal
import logging
from typing import Any, Dict, Optional, Tuple
import httpx

from app.core.config import settings
from app.services.payments.paypal_auth import paypal_auth_service

logger = logging.getLogger(__name__)


class PayPalOrdersClient:
    """Client for interacting with PayPal Orders REST API v2."""

    def __init__(self, auth_service=paypal_auth_service):
        self.auth = auth_service

    @property
    def base_url(self) -> str:
        return settings.PAYPAL_API_BASE_URL.rstrip("/")

    async def _get_auth_headers(self, request_id: Optional[str] = None) -> Dict[str, str]:
        """Assemble authenticated request headers with optional idempotency request ID."""
        token = await self.auth.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Prefer": "return=representation",
        }
        if request_id:
            headers["PayPal-Request-Id"] = request_id
        return headers

    async def create_order(
        self,
        payment_id: str,
        milestone_title: str,
        sequence_number: int,
        amount: Decimal,
        currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """Create a PayPal v2 order with intent CAPTURE."""
        url = f"{self.base_url}/v2/checkout/orders"
        headers = await self._get_auth_headers(request_id=idempotency_key)

        formatted_amount = f"{amount:.2f}"
        clean_title = milestone_title[:100].strip()

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": payment_id,
                    "description": f"Milestone #{sequence_number}: {clean_title}",
                    "custom_id": payment_id,
                    "amount": {
                        "currency_code": currency.upper(),
                        "value": formatted_amount,
                    },
                }
            ],
            "application_context": {
                "brand_name": "MilestonePay AI",
                "landing_page": "NO_PREFERENCE",
                "user_action": "PAY_NOW",
            },
        }

        timeout = httpx.Timeout(settings.PAYPAL_REQUEST_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
            except httpx.RequestError as exc:
                logger.error("Network error creating PayPal order: %s", str(exc))
                raise RuntimeError(f"Network error communicating with PayPal: {exc}")

        if response.status_code not in (200, 201):
            logger.error(
                "PayPal order creation failed (status %d): %s",
                response.status_code,
                response.text,
            )
            raise RuntimeError(
                f"PayPal rejected order creation (HTTP {response.status_code}): {response.text}"
            )

        data = response.json()
        logger.info("Successfully created PayPal order %s for payment %s", data.get("id"), payment_id)
        return data

    async def capture_order(
        self,
        provider_order_id: str,
        idempotency_key: str,
    ) -> Tuple[int, Dict[str, Any]]:
        """Capture an approved PayPal order using the orders/capture endpoint."""
        url = f"{self.base_url}/v2/checkout/orders/{provider_order_id}/capture"
        headers = await self._get_auth_headers(request_id=f"{idempotency_key}-cap")

        timeout = httpx.Timeout(settings.PAYPAL_REQUEST_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, json={}, headers=headers)
            except httpx.RequestError as exc:
                logger.error("Network error capturing PayPal order %s: %s", provider_order_id, str(exc))
                raise RuntimeError(f"Network error capturing PayPal order: {exc}")

        status_code = response.status_code
        data = response.json() if response.text else {}

        # Handle ORDER_ALREADY_CAPTURED gracefully by fetching order details
        if status_code == 422:
            details = data.get("details", [])
            already_captured = any(d.get("issue") == "ORDER_ALREADY_CAPTURED" for d in details)
            if already_captured:
                logger.warning("PayPal order %s was already captured. Fetching existing capture details.", provider_order_id)
                order_details = await self.get_order(provider_order_id)
                return 200, order_details

        if status_code not in (200, 201):
            logger.error(
                "PayPal order capture rejected for %s (status %d): %s",
                provider_order_id,
                status_code,
                response.text,
            )
            raise RuntimeError(
                f"PayPal order capture failed (HTTP {status_code}): {response.text}"
            )

        logger.info("Successfully captured PayPal order %s", provider_order_id)
        return status_code, data

    async def get_order(self, provider_order_id: str) -> Dict[str, Any]:
        """Retrieve complete order details from PayPal."""
        url = f"{self.base_url}/v2/checkout/orders/{provider_order_id}"
        headers = await self._get_auth_headers()

        timeout = httpx.Timeout(settings.PAYPAL_REQUEST_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(url, headers=headers)
            except httpx.RequestError as exc:
                logger.error("Network error fetching PayPal order %s: %s", provider_order_id, str(exc))
                raise RuntimeError(f"Network error retrieving PayPal order: {exc}")

        if response.status_code != 200:
            logger.error("Failed to retrieve PayPal order %s (status %d)", provider_order_id, response.status_code)
            raise RuntimeError(
                f"Failed to retrieve PayPal order {provider_order_id} (HTTP {response.status_code})"
            )

        return response.json()


paypal_orders_client = PayPalOrdersClient()
