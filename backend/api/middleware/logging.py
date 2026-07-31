"""
Request & Response Structured Logging Middleware
Virtual Wear Simulation — Phase 1.4 Production
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from utils.logger import log_structured
except ImportError:
    from backend.utils.logger import log_structured


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        request_id = getattr(request.state, "request_id", None)

        response = await call_next(request)
        process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        log_structured(
            message=f"API Request processed: {request.method} {request.url.path}",
            level="INFO" if response.status_code < 400 else "WARNING",
            request_id=request_id,
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            latency=process_time_ms
        )

        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        return response
