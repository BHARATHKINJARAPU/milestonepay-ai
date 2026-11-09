import asyncio
from datetime import datetime, timezone
import logging
from typing import Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class PayPalAuthService:
    """Manages OAuth 2.0 client credentials authentication and token caching for PayPal REST API."""

    def __init__(self):
        self._cached_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None
        self._lock = asyncio.Lock()

    @property
    def base_url(self) -> str:
        return settings.PAYPAL_API_BASE_URL.rstrip("/")

    @property
    def client_id(self) -> Optional[str]:
        return settings.PAYPAL_CLIENT_ID

    @property
    def client_secret(self) -> Optional[str]:
        return settings.PAYPAL_CLIENT_SECRET

    def is_configured(self) -> bool:
        """Check whether valid PayPal credentials are configured."""
        return bool(self.client_id and self.client_secret)

    def _is_token_valid(self) -> bool:
        """Determine if cached token is still valid with a 60-second safety window."""
        if not self._cached_token or not self._expires_at:
            return False
        # Buffer of 60 seconds before actual expiration
        remaining_seconds = (self._expires_at - datetime.now(timezone.utc)).total_seconds()
        return remaining_seconds > 60

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """Retrieve a valid OAuth access token, caching and refreshing as needed."""
        if not force_refresh and self._is_token_valid():
            return self._cached_token  # type: ignore

        async with self._lock:
            # Double check inside lock
            if not force_refresh and self._is_token_valid():
                return self._cached_token  # type: ignore

            if not self.is_configured():
                raise RuntimeError(
                    "PayPal credentials (PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET) are not configured."
                )

            token_url = f"{self.base_url}/v1/oauth2/token"
            logger.info("Requesting fresh PayPal OAuth 2.0 access token from %s", token_url)

            timeout = httpx.Timeout(settings.PAYPAL_REQUEST_TIMEOUT_SECONDS)
            async with httpx.AsyncClient(timeout=timeout) as client:
                try:
                    response = await client.post(
                        token_url,
                        auth=(self.client_id, self.client_secret),  # type: ignore
                        data={"grant_type": "client_credentials"},
                        headers={
                            "Accept": "application/json",
                            "Accept-Language": "en_US",
                        },
                    )
                except httpx.RequestError as exc:
                    logger.error("Network error while connecting to PayPal OAuth: %s", str(exc))
                    raise RuntimeError(f"Failed to communicate with PayPal OAuth server: {exc}")

            if response.status_code != 200:
                logger.error(
                    "PayPal OAuth token request rejected (status %d): %s",
                    response.status_code,
                    response.text[:300],
                )
                raise RuntimeError(
                    f"PayPal OAuth authentication failed (HTTP {response.status_code}). Verify PayPal Sandbox credentials."
                )

            data = response.json()
            access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)

            if not access_token:
                raise RuntimeError("PayPal OAuth response missing access_token.")

            self._cached_token = access_token
            # Calculate expiration timestamp in UTC
            self._expires_at = datetime.fromtimestamp(
                datetime.now(timezone.utc).timestamp() + expires_in,
                tz=timezone.utc,
            )

            logger.info("Successfully acquired PayPal OAuth access token (valid for %d seconds)", expires_in)
            return self._cached_token

    def clear_cache(self) -> None:
        """Clear cached token (useful for test assertions and reset)."""
        self._cached_token = None
        self._expires_at = None


paypal_auth_service = PayPalAuthService()
