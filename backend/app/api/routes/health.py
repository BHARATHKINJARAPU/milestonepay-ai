import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.health import ErrorResponse, HealthResponse, ReadyResponse

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
    """Execute SELECT 1 against PostgreSQL to verify database connectivity.

    Returns HTTP 200 when connected, or HTTP 503 if unavailable with a sanitized message.
    """
    try:
        # Execute verification query against the connected database
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
        # Log error internally without exposing credentials or full stack traces to the client
        logger.error("PostgreSQL readiness check failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is unavailable. Please verify PostgreSQL connection.",
        ) from None
