"""
Metrics Router — API v1
Virtual Wear Simulation — Phase 1.4 Production
"""

from fastapi import APIRouter, Depends, Request

try:
    from api.dependencies import get_metrics_service
    from models.api_models import MetricsResponse
    from models.base_response import BaseResponse
    from services.metrics_service import MetricsService
except ImportError:
    from backend.api.dependencies import get_metrics_service
    from backend.models.api_models import MetricsResponse
    from backend.models.base_response import BaseResponse
    from backend.services.metrics_service import MetricsService

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


@router.get("", response_model=BaseResponse[MetricsResponse], summary="Get benchmark statistics and analytics")
def get_metrics(
    request: Request,
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    req_id = getattr(request.state, "request_id", None)
    metrics = metrics_service.get_metrics()
    return BaseResponse(
        success=True,
        message="Retrieved system benchmark statistics and analytics",
        data=metrics,
        requestId=req_id
    )
