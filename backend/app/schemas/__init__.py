"""Pydantic schemas package."""

from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.schemas.health import ErrorResponse, HealthResponse, ReadyResponse
from app.schemas.project import (
    AddMemberRequest,
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectStatusUpdateRequest,
    ProjectUpdateRequest,
)

from app.schemas.milestone import (
    CreateManualPlanRequest,
    GenerateMilestonePlanRequest,
    MilestoneInput,
    MilestonePlanListResponse,
    MilestonePlanResponse,
    MilestonePlanReviewResponse,
    MilestoneResponse,
    RequestRevisionRequest,
    UpdateMilestonePlanRequest,
)
from app.schemas.submission import (
    AISubmissionReviewResponse,
    ClientReviewRequest,
    ClientSubmissionReviewResponse,
    CreateSubmissionRequest,
    CriterionEvaluationOutputSchema,
    GeminiDeliverableEvaluationSchema,
    MilestoneSubmissionListResponse,
    MilestoneSubmissionResponse,
    SubmissionEvidenceResponse,
)
from app.schemas.payment import (
    CreatePaymentRequest,
    MockConfirmPaymentRequest,
    PaymentEligibilityResponse,
    PaymentEventResponse,
    PaymentListResponse,
    PaymentResponse,
)
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.schemas.project_activity import (
    ProjectActivityListResponse,
    ProjectActivityResponse,
)
from app.schemas.analytics import (
    CurrencyAmount,
    DashboardAnalyticsResponse,
    DashboardMilestonesSummary,
    DashboardPaymentsSummary,
    DashboardProjectsSummary,
    PaymentAnalyticsResponse,
    ProjectAiSummaryResponse,
)

__all__ = [
    "HealthResponse",
    "ReadyResponse",
    "ErrorResponse",
    "UserRegisterRequest",
    "UserLoginRequest",
    "UserResponse",
    "TokenResponse",
    "PaymentEligibilityResponse",
    "CreatePaymentRequest",
    "MockConfirmPaymentRequest",
    "PaymentEventResponse",
    "PaymentResponse",
    "PaymentListResponse",
    "NotificationResponse",
    "NotificationListResponse",
    "UnreadCountResponse",
    "ProjectActivityResponse",
    "ProjectActivityListResponse",
    "CurrencyAmount",
    "DashboardProjectsSummary",
    "DashboardMilestonesSummary",
    "DashboardPaymentsSummary",
    "DashboardAnalyticsResponse",
    "PaymentAnalyticsResponse",
    "ProjectAiSummaryResponse",
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
    "ProjectStatusUpdateRequest",
    "AddMemberRequest",
    "ProjectMemberResponse",
    "ProjectResponse",
    "ProjectListResponse",
    "GenerateMilestonePlanRequest",
    "CreateManualPlanRequest",
    "UpdateMilestonePlanRequest",
    "RequestRevisionRequest",
    "MilestoneResponse",
    "MilestonePlanResponse",
    "MilestonePlanListResponse",
    "MilestonePlanReviewResponse",
    "MilestoneInput",
    "CreateSubmissionRequest",
    "ClientReviewRequest",
    "SubmissionEvidenceResponse",
    "AISubmissionReviewResponse",
    "ClientSubmissionReviewResponse",
    "MilestoneSubmissionResponse",
    "MilestoneSubmissionListResponse",
    "CriterionEvaluationOutputSchema",
    "GeminiDeliverableEvaluationSchema",
]

