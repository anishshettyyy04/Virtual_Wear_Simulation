from typing import Any, Dict, List

from fastapi import APIRouter, Request

from app.services.ai.engines import DeviceManager, ModelRegistry
from app.services.api.response_builder import ResponseBuilder

router = APIRouter(prefix="/engines", tags=["AI Engine Discovery"])


@router.get(
    "",
    summary="List Registered VTON Engines",
    description=(
        "Discovers registered virtual try-on engines, versions, devices, and licenses."
    ),
    response_description="List of registered try-on engines and metadata",
)
async def list_engines(request: Request) -> Dict[str, Any]:
    """Returns list of registered try-on engines and readiness metadata."""
    registered_names = ModelRegistry.get_registered_engines()
    engine_list: List[Dict[str, Any]] = []

    device_info = DeviceManager.describe()

    for name in registered_names:
        info = ModelRegistry.get_engine_info(name)
        engine_list.append(
            {
                "name": name,
                "status": "ready",
                "registered_version": info.get("registered_version", "1.0.0"),
                "license": info.get("license", "unknown"),
                "device": "cuda" if device_info.get("cuda_available") else "cpu",
                "supported_garment_categories": [
                    "upper_body",
                    "lower_body",
                    "full_body",
                ],
                "metadata": info.get("metadata", {}),
            }
        )

    request_id = getattr(request.state, "request_id", None)
    return ResponseBuilder.success(
        data={"engines": engine_list, "total_engines": len(engine_list)},
        message="Registered try-on engines discovered successfully",
        request_id=request_id,
    )
