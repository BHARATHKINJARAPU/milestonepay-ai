from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter()

# Include health routes
api_router.include_router(health.router)
