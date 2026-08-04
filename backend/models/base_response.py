"""
Standardized API Base Response Model
Virtual Wear Simulation — Phase 1.4 Production
"""

from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """
    Standard API response envelope format across all endpoints.
    """
    success: bool = Field(True, description="Execution success status flag", json_schema_extra={"example": True})
    message: str = Field("Request successful", description="Human-readable response message", json_schema_extra={"example": "Request successful"})
    data: Optional[T] = Field(None, description="Response data payload")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC generation ISO timestamp",
        json_schema_extra={"example": "2026-07-31T22:54:34Z"}
    )
    requestId: Optional[str] = Field(None, description="Unique UUID request tracking ID", json_schema_extra={"example": "c1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c"})
