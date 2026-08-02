from typing import Any, Dict

from fastapi import APIRouter, Depends, Request

from app.api.dependencies.engines import get_tryon_engine
from app.api.dependencies.jobs import get_job_manager
from app.config.settings import settings
from app.schemas.response import HealthResponse
from app.services.ai.engines import DeviceManager, ModelRegistry
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.services.api.response_builder import ResponseBuilder
from app.services.jobs.manager import BackgroundJobManager

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health Check",
    description="Lightweight status check verifying API operational state.",
)
async def get_health() -> HealthResponse:
    """Returns application operational status and version metadata."""
    return HealthResponse(
        success=True,
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
    )


@router.get(
    "/health/ai",
    summary="AI Pipeline Health & Readiness Check",
    description=(
        "Inspects AI try-on engine readiness, background job queue metrics, "
        "and hardware device configuration without loading heavy weights."
    ),
)
async def get_ai_health(
    request: Request,
    engine: BaseTryOnEngine = Depends(get_tryon_engine),
    job_manager: BackgroundJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Returns AI try-on engine operational readiness and device metrics."""
    check_health_fn = getattr(engine, "check_health", None)
    if callable(check_health_fn):
        health_report = await check_health_fn()
        report_data = health_report.model_dump()
    else:
        report_data = {
            "engine_name": getattr(engine, "model_name", "generic"),
            "is_healthy": True,
            "model_files_found": True,
            "execution_device_available": True,
        }

    device_info = DeviceManager.describe()
    registered_engines = ModelRegistry.get_registered_engines()
    job_health = job_manager.get_health()

    ai_health_data = {
        "status": "ready" if report_data.get("is_healthy") else "degraded",
        "active_engine": report_data.get("engine_name", "idm_vton"),
        "registered_engines": registered_engines,
        "device_info": device_info,
        "engine_health": report_data,
        "job_system": job_health,
    }

    request_id = getattr(request.state, "request_id", None)
    return ResponseBuilder.success(
        data=ai_health_data,
        message="AI try-on pipeline health inspected successfully",
        request_id=request_id,
    )
