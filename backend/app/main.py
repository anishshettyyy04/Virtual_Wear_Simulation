from contextlib import asynccontextmanager
import os
import sys
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


try:
    from app.api.v1.router import api_router
    from app.config.settings import settings
    from app.middleware.error_handler import register_exception_handlers
    from app.middleware.request_id import RequestIDMiddleware
    from app.utils.logger import logger
except ImportError:
    from backend.app.api.v1.router import api_router
    from backend.app.config.settings import settings
    from backend.app.middleware.error_handler import register_exception_handlers
    from backend.app.middleware.request_id import RequestIDMiddleware
    from backend.app.utils.logger import logger

try:
    from api.v1.products import router as products_router
    from api.v1.recommendations import router as recommendations_router
    from api.v1.users import router as users_router
    from api.v1.metrics import router as metrics_router
except ImportError:
    from backend.api.v1.products import router as products_router
    from backend.api.v1.recommendations import router as recommendations_router
    from backend.api.v1.users import router as users_router
    from backend.api.v1.metrics import router as metrics_router



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI modern lifespan context manager for startup and shutdown hooks."""
    logger.info(
        f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]"
    )
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "High-performance backend API foundation for AI Virtual Wear Simulation."
    ),
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Attach Request ID Tracing Middleware
app.add_middleware(RequestIDMiddleware)

# Attach CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

# Register Global Error Handlers
register_exception_handlers(app)

# Serve Generated Output Files & Media Static Assets
data_dir = os.path.join(backend_dir, "data")
os.makedirs(data_dir, exist_ok=True)
app.mount("/data", StaticFiles(directory=data_dir), name="data")

# Diagnostic: confirm static mount vs engine output path alignment
logger.info(f"[STARTUP] Static file mount '/data' -> {os.path.abspath(data_dir)}")
logger.info(f"[STARTUP] CWD = {os.getcwd()}")
logger.info(f"[STARTUP] Engine output 'data/processed/renders' -> {os.path.abspath('data/processed/renders')}")

# Register Aggregated API v1 Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Register REST Endpoints (Products, Recommendations, Users, Metrics)
app.include_router(products_router)
app.include_router(recommendations_router)
app.include_router(users_router)
app.include_router(metrics_router)


