from fastapi import APIRouter

from app.config.settings import settings
from app.schemas.response import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health Check",
    description="Lightweight status check verifying API operational state.",
)
async def get_health() -> HealthResponse:
    """Returns application operational status and version metadata."""
    return HealthResponse(
        success=True,
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
