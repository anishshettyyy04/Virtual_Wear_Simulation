"""
Pydantic API Request and Response Models
Virtual Wear Simulation — Phase 1.4 REST API
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    id: str = Field(..., description="Unique product ID", json_schema_extra={"example": "TS001"})
    name: str = Field(..., description="Product name", json_schema_extra={"example": "Classic Black Crewneck T-Shirt"})
    category: str = Field(..., description="Apparel category", json_schema_extra={"example": "tshirt"})
    brand: str = Field(..., description="Brand name", json_schema_extra={"example": "Urban Wear"})
    price: float = Field(..., description="Product price in INR", json_schema_extra={"example": 799.0})
    currency: Optional[str] = Field("INR", description="Currency code", json_schema_extra={"example": "INR"})
    sizes: List[str] = Field(..., description="Available sizes", json_schema_extra={"example": ["S", "M", "L", "XL"]})
    colors: List[str] = Field(..., description="Garment colors", json_schema_extra={"example": ["Black", "Dark Grey"]})
    material: str = Field(..., description="Fabric composition", json_schema_extra={"example": "100% Premium Cotton"})
    fit: str = Field(..., description="Garment cut", json_schema_extra={"example": "regular"})
    style: str = Field(..., description="Fashion style genre", json_schema_extra={"example": "casual"})
    occasion: Union[str, List[str]] = Field(..., description="Wearing occasion(s)", json_schema_extra={"example": ["Daily Wear"]})
    gender: str = Field(..., description="Gender demographic", json_schema_extra={"example": "unisex"})
    season: str = Field(..., description="Seasonality", json_schema_extra={"example": "all-season"})
    image: str = Field(..., description="Image asset path", json_schema_extra={"example": "/assets/products/tshirts/ts001.jpg"})
    description: str = Field(..., description="Garment description", json_schema_extra={"example": "Timeless crewneck t-shirt."})
    rating: Optional[float] = Field(4.5, description="Customer rating (0-5)", json_schema_extra={"example": 4.5})
    reviewsCount: Optional[int] = Field(0, description="Total reviews count", json_schema_extra={"example": 128})
    isAvailable: bool = Field(True, description="Stock availability flag", json_schema_extra={"example": True})
    stock: int = Field(..., description="Available units in stock", json_schema_extra={"example": 45})
    createdAt: str = Field(..., description="Creation ISO timestamp", json_schema_extra={"example": "2026-07-31T00:00:00Z"})
    updatedAt: str = Field(..., description="Modification ISO timestamp", json_schema_extra={"example": "2026-07-31T00:00:00Z"})


class ProductListResponse(BaseModel):
    success: bool = True
    total: int
    products: List[ProductResponse]


class UserResponse(BaseModel):
    userId: str = Field(..., description="Unique user ID", json_schema_extra={"example": "USR001"})
    name: str = Field(..., description="User full name", json_schema_extra={"example": "Aarav Sharma"})
    gender: str = Field(..., description="User gender", json_schema_extra={"example": "men"})
    ageGroup: str = Field(..., description="Age demographic tier", json_schema_extra={"example": "adult"})
    preferredCategories: List[str] = Field(..., description="Favored categories", json_schema_extra={"example": ["tshirt", "jeans"]})
    preferredColors: List[str] = Field(..., description="Favored colors", json_schema_extra={"example": ["Black", "Blue", "Navy"]})
    preferredStyles: List[str] = Field(..., description="Favored styles", json_schema_extra={"example": ["casual", "streetwear"]})
    preferredFit: str = Field(..., description="Favored fit cut", json_schema_extra={"example": "regular"})
    preferredBrands: List[str] = Field(..., description="Favored brands", json_schema_extra={"example": ["Urban Wear", "Denim Co"]})
    preferredMaterials: List[str] = Field(..., description="Favored materials", json_schema_extra={"example": ["100% Premium Cotton"]})
    preferredOccasions: List[str] = Field(..., description="Target occasions", json_schema_extra={"example": ["Daily Wear"]})
    preferredSeasons: List[str] = Field(..., description="Favored seasons", json_schema_extra={"example": ["all-season", "summer"]})
    budgetRange: Dict[str, float] = Field(..., description="Min and max price boundaries", json_schema_extra={"example": {"min": 500.0, "max": 3000.0}})
    budgetTier: str = Field(..., description="Budget tier classification", json_schema_extra={"example": "medium"})
    favoriteSizes: List[str] = Field(..., description="Standard garment sizes", json_schema_extra={"example": ["M", "L"]})
    height: float = Field(..., description="User height in cm", json_schema_extra={"example": 178.0})
    weight: float = Field(..., description="User weight in kg", json_schema_extra={"example": 72.0})
    bodyType: str = Field(..., description="Body build classification", json_schema_extra={"example": "regular"})
    wishlist: List[str] = Field(..., description="Saved product IDs", json_schema_extra={"example": ["TS001", "JN001"]})
    purchaseHistory: List[str] = Field(..., description="Purchased product IDs", json_schema_extra={"example": ["TS001"]})
    recommendationHistory: List[str] = Field(..., description="Previously recommended product IDs", json_schema_extra={"example": ["TS001"]})
    location: Optional[Dict[str, str]] = Field(None, description="User location object")
    climate: Optional[str] = Field(None, description="Climate zone")
    favoriteColorsFrequency: Optional[Dict[str, int]] = Field(None, description="Color frequency counts")
    interactionMetrics: Optional[Dict[str, int]] = Field(None, description="Catalog interaction metrics")
    lastPreferenceUpdate: Optional[str] = Field(None, description="Last update timestamp")
    createdAt: str = Field(..., description="Creation ISO timestamp")
    updatedAt: str = Field(..., description="Modification ISO timestamp")


class RecommendationRequest(BaseModel):
    userId: str = Field(..., description="Target user identifier", json_schema_extra={"example": "USR001"})
    limit: Optional[int] = Field(10, description="Max recommendations count", json_schema_extra={"example": 10}, ge=1, le=50)
    forceRefresh: Optional[bool] = Field(False, description="Bypass cache flag", json_schema_extra={"example": False})


class RecommendationItemResponse(BaseModel):
    productId: str = Field(..., json_schema_extra={"example": "TS001"})
    name: str = Field(..., json_schema_extra={"example": "Classic Black Crewneck T-Shirt"})
    category: str = Field(..., json_schema_extra={"example": "tshirt"})
    brand: str = Field(..., json_schema_extra={"example": "Urban Wear"})
    price: float = Field(..., json_schema_extra={"example": 799.0})
    currency: Optional[str] = Field("INR", json_schema_extra={"example": "INR"})
    image: str = Field(..., json_schema_extra={"example": "/assets/products/tshirts/ts001.jpg"})
    rating: Optional[float] = Field(4.5, json_schema_extra={"example": 4.5})
    score: float = Field(..., description="Recommendation score [0, 100]", json_schema_extra={"example": 94.5})
    reasons: List[str] = Field(..., description="Human-readable match reasons", json_schema_extra={"example": ["Matches preferred category", "Within budget"]})


class RecommendationResponse(BaseModel):
    success: bool = True
    message: str = Field("Recommendations generated successfully", json_schema_extra={"example": "Recommendations generated successfully"})
    engineVersion: str = Field("1.0.0", json_schema_extra={"example": "1.0.0"})
    strategy: str = Field("RuleBased", json_schema_extra={"example": "RuleBased"})
    configVersion: str = Field("1.0", json_schema_extra={"example": "1.0"})
    executionTimeMs: float = Field(..., json_schema_extra={"example": 1.85})
    productsScanned: int = Field(..., json_schema_extra={"example": 25})
    productsFiltered: int = Field(..., json_schema_extra={"example": 17})
    recommendationsReturned: int = Field(..., json_schema_extra={"example": 10})
    userId: str = Field(..., json_schema_extra={"example": "USR001"})
    generatedAt: str = Field(..., json_schema_extra={"example": "2026-07-31T22:37:47.123456+00:00"})
    recommendations: List[RecommendationItemResponse]


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    products: str = Field(..., json_schema_extra={"example": "loaded"})
    users: str = Field(..., json_schema_extra={"example": "loaded"})
    configuration: str = Field(..., json_schema_extra={"example": "loaded"})
    strategy: str = Field(..., json_schema_extra={"example": "RuleBased"})
    cache: str = Field(..., json_schema_extra={"example": "enabled"})
    analytics: str = Field(..., json_schema_extra={"example": "available"})


class MetricsResponse(BaseModel):
    success: bool = True
    benchmarkSummary: Dict[str, Any]
    analytics: Dict[str, Any]
