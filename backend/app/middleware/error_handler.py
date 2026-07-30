from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.response import ErrorPayload, StandardErrorResponse
from app.utils.logger import logger


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers enforcing standardized API error payloads."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "N/A")
        code = "NOT_FOUND" if exc.status_code == 404 else f"HTTP_{exc.status_code}"

        logger.warning(
            f"HTTP {exc.status_code} [{code}] | RequestID: {request_id} | "
            f"Path: {request.url.path} | Detail: {exc.detail}"
        )

        response_body = StandardErrorResponse(
            success=False,
            error=ErrorPayload(
                code=code,
                message=str(exc.detail) or "The requested resource was not found.",
            ),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response_body.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "N/A")
        logger.warning(
            f"Validation Error [VALIDATION_ERROR] | RequestID: {request_id} | "
            f"Path: {request.url.path} | Errors: {exc.errors()}"
        )

        response_body = StandardErrorResponse(
            success=False,
            error=ErrorPayload(
                code="VALIDATION_ERROR",
                message="Invalid request body or query parameters.",
            ),
        )
        return JSONResponse(
            status_code=422,
            content=response_body.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "N/A")
        logger.error(
            f"Unhandled Internal Failure [INTERNAL_SERVER_ERROR] | "
            f"RequestID: {request_id} | Path: {request.url.path} | Exception: {exc}",
            exc_info=True,
        )

        response_body = StandardErrorResponse(
            success=False,
            error=ErrorPayload(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred.",
            ),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_body.model_dump(),
        )
