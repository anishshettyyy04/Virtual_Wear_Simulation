from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse


class ErrorCode:
    """Standardized machine-readable error codes for Virtual Wear API."""

    INVALID_IMAGE = "INVALID_IMAGE"
    INVALID_CATEGORY = "INVALID_CATEGORY"
    INVALID_ENGINE = "INVALID_ENGINE"
    WEIGHTS_MISSING = "WEIGHTS_MISSING"
    DEVICE_UNAVAILABLE = "DEVICE_UNAVAILABLE"
    ENGINE_INITIALIZATION_FAILED = "ENGINE_INITIALIZATION_FAILED"
    PIPELINE_FAILED = "PIPELINE_FAILED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ResponseBuilder:
    """Centralized response serialization layer for virtual try-on API."""

    API_VERSION = "v1"
    PIPELINE_VERSION = "1.0.0"
    ENGINE_VERSION = "1.0.0"

    @classmethod
    def success(
        cls,
        data: Dict[str, Any],
        message: str = "Request processed successfully",
        request_id: Optional[str] = None,
        request_duration_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Constructs standardized success envelope dictionary."""
        payload: Dict[str, Any] = {
            "success": True,
            "message": message,
            "api_version": cls.API_VERSION,
            "pipeline_version": cls.PIPELINE_VERSION,
            "engine_version": cls.ENGINE_VERSION,
            "data": data,
        }
        if request_id:
            payload["request_id"] = request_id
        if request_duration_ms is not None:
            payload["request_duration_ms"] = round(request_duration_ms, 2)
        return payload

    @classmethod
    def error(
        cls,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None,
        request_id: Optional[str] = None,
    ) -> JSONResponse:
        """Constructs standardized error JSONResponse with error code."""
        error_payload: Dict[str, Any] = {
            "code": code,
            "message": message,
        }
        if details:
            error_payload["details"] = details
        if request_id:
            error_payload["request_id"] = request_id

        payload = {
            "success": False,
            "api_version": cls.API_VERSION,
            "pipeline_version": cls.PIPELINE_VERSION,
            "engine_version": cls.ENGINE_VERSION,
            "error": error_payload,
        }
        return JSONResponse(status_code=status_code, content=payload)
