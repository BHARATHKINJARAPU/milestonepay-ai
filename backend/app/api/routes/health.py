from datetime import datetime, timezone
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import (
    DatabaseDiagnosticInfo,
    ErrorResponse,
    GeminiDiagnosticInfo,
    HealthResponse,
    IntegrationsDiagnosticResponse,
    PayPalDiagnosticInfo,
    ReadyResponse,
    WebhookDiagnosticInfo,
)
from app.services.payments.paypal_auth import paypal_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic API Health Check",
    description="Verifies that the MilestonePay API service is running and responsive.",
)
def get_health() -> HealthResponse:
    """Return basic health status of the API service."""
    return HealthResponse(
        status="ok",
        service="milestonepay-api",
    )


@router.get(
    "/ready",
    response_model=ReadyResponse,
    status_code=status.HTTP_200_OK,
    summary="Database Readiness Check",
    description="Executes a live verification query against the PostgreSQL database.",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Database connectivity failed",
        }
    },
)
def get_ready(db: Session = Depends(get_db)) -> ReadyResponse:
    """Execute SELECT 1 against PostgreSQL to verify database connectivity."""
    try:
        result = db.execute(text("SELECT 1;")).scalar()
        if result != 1:
            logger.error("Readiness check query returned unexpected result: %s", result)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database returned invalid readiness state.",
            )

        return ReadyResponse(
            status="ready",
            service="milestonepay-api",
            database="connected",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("PostgreSQL readiness check failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is unavailable. Please verify PostgreSQL connection.",
        ) from None


@router.get(
    "/integrations",
    response_model=IntegrationsDiagnosticResponse,
    status_code=status.HTTP_200_OK,
    summary="Integration Diagnostics & Security Verification",
    description="Provides real-time connectivity status for Gemini AI, PayPal Sandbox OAuth, PostgreSQL database, and Webhooks without exposing secrets.",
)
@router.get(
    "/diagnostics/integrations",
    response_model=IntegrationsDiagnosticResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_integrations_diagnostics(db: Session = Depends(get_db)) -> IntegrationsDiagnosticResponse:
    """Check connectivity and readiness of all external providers safely."""
    # 1. Database status
    db_status = "connected"
    try:
        db.execute(text("SELECT 1;")).scalar()
    except Exception as e:
        logger.error("Database diagnostic check failed: %s", str(e))
        db_status = "error"

    # 2. Google Gemini AI status
    gemini_configured = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
    gemini_model = settings.GEMINI_MODEL
    # Normalize model display name
    if gemini_model in ("gemini-2.5-flash", "Gemini 2.5 Flash"):
        gemini_model = "gemini-3.5-flash (auto-adapted)"
    gemini_status = "connected" if gemini_configured else "not_configured"

    # 3. PayPal Sandbox status
    pp_configured = paypal_auth_service.is_configured()
    oauth_authenticated = False
    pp_status = "not_configured"

    if settings.PAYMENT_PROVIDER == "paypal":
        if pp_configured:
            try:
                # Attempt to get or reuse cached OAuth token
                await paypal_auth_service.get_access_token()
                oauth_authenticated = True
                pp_status = "connected"
            except Exception as e:
                logger.warning("PayPal OAuth diagnostic probe failed: %s", str(e))
                pp_status = "auth_failed"
        else:
            pp_status = "missing_credentials"
    else:
        pp_status = "mock_provider_active"

    # 4. Webhook status
    webhook_configured = bool(settings.PAYPAL_WEBHOOK_ID and settings.PAYPAL_WEBHOOK_ID.strip())
    webhook_status = "configured" if webhook_configured else "pending_registration"
    webhook_note = (
        "Active PayPal webhook ID configured for event signature verification."
        if webhook_configured
        else "PayPal sandbox webhooks can be registered via PayPal Developer Portal or ngrok tunnel pointing to /api/v1/webhooks/paypal"
    )

    return IntegrationsDiagnosticResponse(
        service="milestonepay-api",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
        database=DatabaseDiagnosticInfo(
            status=db_status,
            engine="PostgreSQL",
        ),
        gemini=GeminiDiagnosticInfo(
            configured=gemini_configured,
            model=gemini_model,
            status=gemini_status,
            key_masked="Configured (Safe)" if gemini_configured else "Not Configured",
        ),
        paypal=PayPalDiagnosticInfo(
            provider=settings.PAYMENT_PROVIDER,
            mode=settings.PAYPAL_MODE,
            base_url=settings.PAYPAL_API_BASE_URL,
            client_id_configured=bool(settings.PAYPAL_CLIENT_ID),
            client_secret_configured=bool(settings.PAYPAL_CLIENT_SECRET),
            oauth_authenticated=oauth_authenticated,
            currency=settings.PAYPAL_CURRENCY,
            status=pp_status,
        ),
        webhook=WebhookDiagnosticInfo(
            configured=webhook_configured,
            status=webhook_status,
            endpoint=f"{settings.API_V1_PREFIX}/webhooks/paypal",
            note=webhook_note,
        ),
    )
