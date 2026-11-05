from fastapi import APIRouter

from app.api.routes import auth, health, projects

api_router = APIRouter()

# Include routes
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(projects.router)

