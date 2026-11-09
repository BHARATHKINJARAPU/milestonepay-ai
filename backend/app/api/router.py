from fastapi import APIRouter

from app.api.routes import (
    analytics,
    auth,
    health,
    milestones,
    notifications,
    payments,
    projects,
    submissions,
)

api_router = APIRouter()

# Include routes
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(milestones.router)
api_router.include_router(submissions.router)
api_router.include_router(payments.router)
api_router.include_router(notifications.router)
api_router.include_router(analytics.router)

