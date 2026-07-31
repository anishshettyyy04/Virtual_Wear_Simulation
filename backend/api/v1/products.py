"""
Products Router — API v1
Virtual Wear Simulation — Phase 1.4 Production
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

try:
    from api.dependencies import get_product_service
    from models.api_models import ProductResponse
    from models.base_response import BaseResponse
    from services.product_service import ProductService
except ImportError:
    from backend.api.dependencies import get_product_service
    from backend.models.api_models import ProductResponse
    from backend.models.base_response import BaseResponse
    from backend.services.product_service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("", response_model=BaseResponse[List[ProductResponse]], summary="List all products")
def get_products(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by apparel category"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    product_service: ProductService = Depends(get_product_service)
):
    req_id = getattr(request.state, "request_id", None)
    products = product_service.get_all_products(category=category, gender=gender)
    return BaseResponse(
        success=True,
        message=f"Retrieved {len(products)} products",
        data=products,
        requestId=req_id
    )


@router.get("/{productId}", response_model=BaseResponse[ProductResponse], summary="Get single product by ID")
def get_product_by_id(
    productId: str,
    request: Request,
    product_service: ProductService = Depends(get_product_service)
):
    req_id = getattr(request.state, "request_id", None)
    product = product_service.get_product_by_id(productId)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{productId}' not found"
        )
    return BaseResponse(
        success=True,
        message=f"Retrieved product '{productId}'",
        data=product,
        requestId=req_id
    )
