"""
Health Router — API v1
Virtual Wear Simulation — Phase 1.4 Production
"""

from fastapi import APIRouter, Depends, Request

try:
    from api.dependencies import get_health_service
    from models.api_models import HealthResponse
    from models.base_response import BaseResponse
    from services.health_service import HealthService
except ImportError:
    from backend.api.dependencies import get_health_service
    from backend.models.api_models import HealthResponse
    from backend.models.base_response import BaseResponse
    from backend.services.health_service import HealthService

router = APIRouter(prefix="/api/v1/health", tags=["Health"])


@router.get("", response_model=BaseResponse[HealthResponse], summary="Check system health status")
def get_health(
    request: Request,
    health_service: HealthService = Depends(get_health_service)
):
    req_id = getattr(request.state, "request_id", None)
    health = health_service.get_health_status()
    return BaseResponse(
        success=health.get("status") in ["healthy", "degraded"],
        message="System health check status",
        data=health,
        requestId=req_id
    )
