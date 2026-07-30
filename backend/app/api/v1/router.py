from fastapi import APIRouter

from app.api.v1.routes import health

api_router = APIRouter()

# Register aggregated route modules
api_router.include_router(health.router)
