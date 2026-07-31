"""
Users Router — API v1
Virtual Wear Simulation — Phase 1.4 Production
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from api.dependencies import get_user_service
    from models.api_models import UserResponse
    from models.base_response import BaseResponse
    from services.user_service import UserService
except ImportError:
    from backend.api.dependencies import get_user_service
    from backend.models.api_models import UserResponse
    from backend.models.base_response import BaseResponse
    from backend.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/{userId}", response_model=BaseResponse[UserResponse], summary="Get user preference profile")
def get_user_by_id(
    userId: str,
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    req_id = getattr(request.state, "request_id", None)
    user = user_service.get_user_by_id(userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{userId}' not found"
        )
    return BaseResponse(
        success=True,
        message=f"Retrieved user preference profile '{userId}'",
        data=user,
        requestId=req_id
    )
