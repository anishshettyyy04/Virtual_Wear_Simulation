"""
Pydantic API Request and Response Models
Virtual Wear Simulation — Phase 1.4 REST API
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    id: str = Field(..., description="Unique product ID", example="TS001")
    name: str = Field(..., description="Product name", example="Classic Black Crewneck T-Shirt")
    category: str = Field(..., description="Apparel category", example="tshirt")
    brand: str = Field(..., description="Brand name", example="Urban Wear")
    price: float = Field(..., description="Product price in INR", example=799.0)
    currency: Optional[str] = Field("INR", description="Currency code", example="INR")
    sizes: List[str] = Field(..., description="Available sizes", example=["S", "M", "L", "XL"])
    colors: List[str] = Field(..., description="Garment colors", example=["Black", "Dark Grey"])
    material: str = Field(..., description="Fabric composition", example="100% Premium Cotton")
    fit: str = Field(..., description="Garment cut", example="regular")
    style: str = Field(..., description="Fashion style genre", example="casual")
    occasion: Union[str, List[str]] = Field(..., description="Wearing occasion(s)", example=["Daily Wear"])
    gender: str = Field(..., description="Gender demographic", example="unisex")
    season: str = Field(..., description="Seasonality", example="all-season")
    image: str = Field(..., description="Image asset path", example="/assets/products/tshirts/ts001.jpg")
    description: str = Field(..., description="Garment description", example="Timeless crewneck t-shirt.")
    rating: Optional[float] = Field(4.5, description="Customer rating (0-5)", example=4.5)
    reviewsCount: Optional[int] = Field(0, description="Total reviews count", example=128)
    isAvailable: bool = Field(True, description="Stock availability flag", example=True)
    stock: int = Field(..., description="Available units in stock", example=45)
    createdAt: str = Field(..., description="Creation ISO timestamp", example="2026-07-31T00:00:00Z")
    updatedAt: str = Field(..., description="Modification ISO timestamp", example="2026-07-31T00:00:00Z")


class ProductListResponse(BaseModel):
    success: bool = True
    total: int
    products: List[ProductResponse]


class UserResponse(BaseModel):
    userId: str = Field(..., description="Unique user ID", example="USR001")
    name: str = Field(..., description="User full name", example="Aarav Sharma")
    gender: str = Field(..., description="User gender", example="men")
    ageGroup: str = Field(..., description="Age demographic tier", example="adult")
    preferredCategories: List[str] = Field(..., description="Favored categories", example=["tshirt", "jeans"])
    preferredColors: List[str] = Field(..., description="Favored colors", example=["Black", "Blue", "Navy"])
    preferredStyles: List[str] = Field(..., description="Favored styles", example=["casual", "streetwear"])
    preferredFit: str = Field(..., description="Favored fit cut", example="regular")
    preferredBrands: List[str] = Field(..., description="Favored brands", example=["Urban Wear", "Denim Co"])
    preferredMaterials: List[str] = Field(..., description="Favored materials", example=["100% Premium Cotton"])
    preferredOccasions: List[str] = Field(..., description="Target occasions", example=["Daily Wear"])
    preferredSeasons: List[str] = Field(..., description="Favored seasons", example=["all-season", "summer"])
    budgetRange: Dict[str, float] = Field(..., description="Min and max price boundaries", example={"min": 500.0, "max": 3000.0})
    budgetTier: str = Field(..., description="Budget tier classification", example="medium")
    favoriteSizes: List[str] = Field(..., description="Standard garment sizes", example=["M", "L"])
    height: float = Field(..., description="User height in cm", example=178.0)
    weight: float = Field(..., description="User weight in kg", example=72.0)
    bodyType: str = Field(..., description="Body build classification", example="regular")
    wishlist: List[str] = Field(..., description="Saved product IDs", example=["TS001", "JN001"])
    purchaseHistory: List[str] = Field(..., description="Purchased product IDs", example=["TS001"])
    recommendationHistory: List[str] = Field(..., description="Previously recommended product IDs", example=["TS001"])
    location: Optional[Dict[str, str]] = Field(None, description="User location object")
    climate: Optional[str] = Field(None, description="Climate zone")
    favoriteColorsFrequency: Optional[Dict[str, int]] = Field(None, description="Color frequency counts")
    interactionMetrics: Optional[Dict[str, int]] = Field(None, description="Catalog interaction metrics")
    lastPreferenceUpdate: Optional[str] = Field(None, description="Last update timestamp")
    createdAt: str = Field(..., description="Creation ISO timestamp")
    updatedAt: str = Field(..., description="Modification ISO timestamp")


class RecommendationRequest(BaseModel):
    userId: str = Field(..., description="Target user identifier", example="USR001")
    limit: Optional[int] = Field(10, description="Max recommendations count", example=10, ge=1, le=50)
    forceRefresh: Optional[bool] = Field(False, description="Bypass cache flag", example=False)


class RecommendationItemResponse(BaseModel):
    productId: str = Field(..., example="TS001")
    name: str = Field(..., example="Classic Black Crewneck T-Shirt")
    category: str = Field(..., example="tshirt")
    brand: str = Field(..., example="Urban Wear")
    price: float = Field(..., example=799.0)
    currency: Optional[str] = Field("INR", example="INR")
    image: str = Field(..., example="/assets/products/tshirts/ts001.jpg")
    rating: Optional[float] = Field(4.5, example=4.5)
    score: float = Field(..., description="Recommendation score [0, 100]", example=94.5)
    reasons: List[str] = Field(..., description="Human-readable match reasons", example=["Matches preferred category", "Within budget"])


class RecommendationResponse(BaseModel):
    success: bool = True
    message: str = Field("Recommendations generated successfully", example="Recommendations generated successfully")
    engineVersion: str = Field("1.0.0", example="1.0.0")
    strategy: str = Field("RuleBased", example="RuleBased")
    configVersion: str = Field("1.0", example="1.0")
    executionTimeMs: float = Field(..., example=1.85)
    productsScanned: int = Field(..., example=25)
    productsFiltered: int = Field(..., example=17)
    recommendationsReturned: int = Field(..., example=10)
    userId: str = Field(..., example="USR001")
    generatedAt: str = Field(..., example="2026-07-31T22:37:47.123456+00:00")
    recommendations: List[RecommendationItemResponse]


class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    products: str = Field(..., example="loaded")
    users: str = Field(..., example="loaded")
    configuration: str = Field(..., example="loaded")
    strategy: str = Field(..., example="RuleBased")
    cache: str = Field(..., example="enabled")
    analytics: str = Field(..., example="available")


class MetricsResponse(BaseModel):
    success: bool = True
    benchmarkSummary: Dict[str, Any]
    analytics: Dict[str, Any]
