from fastapi import APIRouter

from app.api.v1.routes import engines, health, jobs, tryon

api_router = APIRouter()

# Register aggregated route modules
api_router.include_router(health.router)
api_router.include_router(engines.router)
api_router.include_router(tryon.router)
api_router.include_router(jobs.router)
