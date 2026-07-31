"""
Global Exception Handler Middleware
Virtual Wear Simulation — Phase 1.4 Production
"""

from datetime import datetime, timezone
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    from utils.logger import log_structured
except ImportError:
    from backend.utils.logger import log_structured


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    req_id = getattr(request.state, "request_id", None)
    log_structured(
        message=f"HTTP Exception: {exc.status_code} — {exc.detail}",
        level="WARNING",
        request_id=req_id,
        endpoint=request.url.path,
        method=request.method,
        status_code=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requestId": req_id
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", None)
    log_structured(
        message=f"Validation Error: {exc.errors()}",
        level="WARNING",
        request_id=req_id,
        endpoint=request.url.path,
        method=request.method,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Request validation error",
            "data": {"errors": exc.errors()},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requestId": req_id
        }
    )


async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", None)
    log_structured(
        message=f"Unhandled Exception: {str(exc)}",
        level="ERROR",
        request_id=req_id,
        endpoint=request.url.path,
        method=request.method,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal Server Error",
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requestId": req_id
        }
    )
