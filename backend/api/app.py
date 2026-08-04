"""
FastAPI Application Server Entry Point with Startup Validation & Middleware
Virtual Wear Simulation — Phase 1.4 Production
"""

from contextlib import asynccontextmanager
import os
import sys

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    from api.middleware.cors import setup_cors
    from api.middleware.exception_handler import (
        global_exception_handler,
        http_exception_handler,
        validation_exception_handler
    )
    from api.middleware.logging import LoggingMiddleware
    from api.middleware.rate_limit import RateLimitMiddleware
    from api.middleware.request_id import RequestIdMiddleware
    from api.v1 import health, metrics, products, recommendations, users
    from config.settings import settings
    from recommendation.health import check_system_health
    from utils.logger import log_structured, logger
except ImportError:
    from backend.api.middleware.cors import setup_cors
    from backend.api.middleware.exception_handler import (
        global_exception_handler,
        http_exception_handler,
        validation_exception_handler
    )
    from backend.api.middleware.logging import LoggingMiddleware
    from backend.api.middleware.rate_limit import RateLimitMiddleware
    from backend.api.middleware.request_id import RequestIdMiddleware
    from backend.api.v1 import health, metrics, products, recommendations, users
    from backend.config.settings import settings
    from backend.recommendation.health import check_system_health
    from backend.utils.logger import log_structured, logger


def perform_startup_validation():
    """
    Validates critical system dependencies on FastAPI application startup.
    Fails startup with RuntimeError if critical dependencies are missing.
    """
    logger.info("Executing startup validation checks...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    prod_file = os.path.join(base_dir, 'data', 'products.json')
    user_file = os.path.join(base_dir, 'data', 'user_preferences.json')
    config_file = os.path.join(base_dir, 'config', 'recommendation_config.json')

    if not os.path.exists(prod_file):
        msg = f"CRITICAL STARTUP ERROR: Product dataset missing at '{prod_file}'"
        logger.error(msg)
        raise RuntimeError(msg)

    if not os.path.exists(user_file):
        msg = f"CRITICAL STARTUP ERROR: User preference dataset missing at '{user_file}'"
        logger.error(msg)
        raise RuntimeError(msg)

    if not os.path.exists(config_file):
        msg = f"CRITICAL STARTUP ERROR: Recommendation config missing at '{config_file}'"
        logger.error(msg)
        raise RuntimeError(msg)

    health_status = check_system_health()
    if health_status.get("status") == "unhealthy":
        msg = f"CRITICAL STARTUP ERROR: System health check failed: {health_status}"
        logger.error(msg)
        raise RuntimeError(msg)

    log_structured("Startup validation passed cleanly! All subsystems operational.", level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    perform_startup_validation()
    log_structured("Virtual Wear Simulation REST API Server online.", level="INFO")
    yield
    log_structured("Shutting down Virtual Wear Simulation REST API Server...", level="INFO")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.4.0",
        description=(
            "Production-ready backend REST API with API versioning (v1), Request ID tracing, "
            "structured logging, OpenAPI documentation, and AI Virtual Try-On integration readiness."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # Setup Middleware
    setup_cors(app)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # Register Exception Handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # Mount Versioned API Routers
    app.include_router(products.router)
    app.include_router(users.router)
    app.include_router(recommendations.router)
    app.include_router(health.router)
    app.include_router(metrics.router)

    return app


app = create_app()
