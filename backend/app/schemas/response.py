from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Explicit response model for GET /api/v1/health."""

    success: bool = Field(default=True, json_schema_extra={"example": True})
    status: str = Field(default="healthy", json_schema_extra={"example": "healthy"})
    service: str = Field(
        ..., json_schema_extra={"example": "Virtual Wear Simulation API"}
    )
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})


class ErrorPayload(BaseModel):
    """Error details payload containing machine code and human message."""

    code: str = Field(..., json_schema_extra={"example": "NOT_FOUND"})
    message: str = Field(
        ...,
        json_schema_extra={"example": "The requested endpoint was not found."},
    )


class StandardErrorResponse(BaseModel):
    """Standardized error response structure across all backend APIs."""

    success: bool = Field(default=False, json_schema_extra={"example": False})
    error: ErrorPayload


class StandardSuccessResponse(BaseModel, Generic[T]):
    """Generic wrapper for successful API responses."""

    success: bool = Field(default=True, json_schema_extra={"example": True})
    data: Optional[T] = Field(default=None)
    message: str = Field(default="Request completed successfully")
