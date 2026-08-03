"""
Recommendations Router — API v1
Virtual Wear Simulation — Phase 1.4 Production
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from api.dependencies import get_recommendation_service
    from models.api_models import RecommendationRequest, RecommendationResponse
    from models.base_response import BaseResponse
    from services.recommendation_service import RecommendationService
except ImportError:
    from backend.api.dependencies import get_recommendation_service
    from backend.models.api_models import RecommendationRequest, RecommendationResponse
    from backend.models.base_response import BaseResponse
    from backend.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendations"])


@router.post("", response_model=BaseResponse[RecommendationResponse], summary="Generate personalized product recommendations")
def generate_recommendations(
    payload: RecommendationRequest,
    request: Request,
    rec_service: RecommendationService = Depends(get_recommendation_service)
):
    req_id = getattr(request.state, "request_id", None)
    res = rec_service.generate_recommendations(
        user_id=payload.userId,
        limit=payload.limit,
        force_refresh=payload.forceRefresh
    )

    if not res.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("message", f"User ID '{payload.userId}' not found")
        )

    return BaseResponse(
        success=True,
        message="Recommendations generated successfully",
        data=res,
        requestId=req_id
    )
