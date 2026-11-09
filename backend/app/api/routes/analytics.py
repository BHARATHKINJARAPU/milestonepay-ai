import logging
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import (
    DashboardAnalyticsResponse,
    PaymentAnalyticsResponse,
    ProjectAiSummaryResponse,
)
from app.services.analytics_service import analytics_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics & Insights"])


@router.get(
    "/dashboard",
    response_model=DashboardAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get role-specific dashboard analytics",
    description="Calculates real PostgreSQL project, milestone, and financial metrics for the current user.",
)
def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardAnalyticsResponse:
    """Retrieve comprehensive dashboard stats tailored to current user role."""
    return analytics_service.get_dashboard_analytics(db=db, current_user=current_user)


@router.get(
    "/payments",
    response_model=PaymentAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get payment analytics and trends",
    description="Returns currency-grouped payment insights and daily settlement trends.",
)
def get_payment_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentAnalyticsResponse:
    """Retrieve detailed payment metrics and trends for user projects."""
    return analytics_service.get_payment_analytics(db=db, current_user=current_user)


@router.get(
    "/projects/{project_id}/ai-summary",
    response_model=ProjectAiSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Gemini AI-generated project summary and health evaluation",
    description="Synthesizes factual project records using Gemini, with graceful fallback if AI is unavailable.",
)
def get_project_ai_summary(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectAiSummaryResponse:
    """Generate or retrieve structured AI project health assessment."""
    return analytics_service.get_project_ai_summary(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )

