from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.services.ai.engines.common.exceptions import (
    DeviceUnavailableError,
    EngineInitializationError,
    InferenceError,
    WeightMissingError,
)
from app.services.ai.exceptions import AIPipelineError
from app.services.api.response_builder import ErrorCode, ResponseBuilder
from app.utils.logger import logger


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers enforcing standardized API error payloads."""

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        msg = str(exc)
        code = ErrorCode.VALIDATION_ERROR
        if "category" in msg.lower():
            code = ErrorCode.INVALID_CATEGORY
        elif "engine" in msg.lower():
            code = ErrorCode.INVALID_ENGINE
        elif "image" in msg.lower() or "file" in msg.lower() or "mime" in msg.lower():
            code = ErrorCode.INVALID_IMAGE

        logger.warning(f"ValueError [{code}] | RequestID: {request_id} | Detail: {msg}")
        return ResponseBuilder.error(
            code=code,
            message=msg,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            request_id=request_id,
        )

    @app.exception_handler(WeightMissingError)
    async def weight_missing_handler(
        request: Request, exc: WeightMissingError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.error(
            f"WeightMissingError [WEIGHTS_MISSING] | ReqID: {request_id} | {exc}"
        )
        return ResponseBuilder.error(
            code=ErrorCode.WEIGHTS_MISSING,
            message=exc.message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"missing_assets": exc.missing_assets},
            request_id=request_id,
        )

    @app.exception_handler(DeviceUnavailableError)
    async def device_unavailable_handler(
        request: Request, exc: DeviceUnavailableError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.error(
            f"DeviceUnavailableError [DEVICE_UNAVAILABLE] | ReqID: {request_id} | {exc}"
        )
        return ResponseBuilder.error(
            code=ErrorCode.DEVICE_UNAVAILABLE,
            message=exc.message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"requested_device": exc.requested_device},
            request_id=request_id,
        )

    @app.exception_handler(EngineInitializationError)
    async def engine_init_handler(
        request: Request, exc: EngineInitializationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.error(
            f"EngineInitializationError [ENGINE_INITIALIZATION_FAILED] | "
            f"RequestID: {request_id} | Detail: {exc}"
        )
        return ResponseBuilder.error(
            code=ErrorCode.ENGINE_INITIALIZATION_FAILED,
            message=exc.message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
        )

    @app.exception_handler(InferenceError)
    @app.exception_handler(AIPipelineError)
    async def ai_pipeline_handler(
        request: Request, exc: AIPipelineError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.error(f"AIPipelineError [PIPELINE_FAILED] | ReqID: {request_id} | {exc}")
        return ResponseBuilder.error(
            code=ErrorCode.PIPELINE_FAILED,
            message=exc.message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        code = "NOT_FOUND" if exc.status_code == 404 else f"HTTP_{exc.status_code}"

        logger.warning(
            f"HTTP {exc.status_code} [{code}] | RequestID: {request_id} | "
            f"Path: {request.url.path} | Detail: {exc.detail}"
        )
        return ResponseBuilder.error(
            code=code,
            message=str(exc.detail) or "The requested resource was not found.",
            status_code=exc.status_code,
            request_id=request_id,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.warning(
            f"Validation Error [VALIDATION_ERROR] | RequestID: {request_id} | "
            f"Path: {request.url.path} | Errors: {exc.errors()}"
        )
        return ResponseBuilder.error(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid request body or parameters.",
            status_code=422,
            details=exc.errors(),
            request_id=request_id,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.error(
            f"Unhandled Internal Failure [INTERNAL_ERROR] | "
            f"RequestID: {request_id} | Path: {request.url.path} | Exception: {exc}",
            exc_info=True,
        )
        return ResponseBuilder.error(
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected internal server error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
        )
