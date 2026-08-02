import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from app.api.dependencies.pipeline import get_virtual_wear_pipeline
from app.schemas.ai import GarmentInput, PersonInput
from app.services.ai.pipeline import VirtualWearPipeline
from app.services.api.request_validator import RequestValidator
from app.services.api.response_builder import ResponseBuilder
from app.services.api.upload_service import UploadService
from app.utils.logger import logger

router = APIRouter(prefix="/tryon", tags=["Virtual Try-On"])


@router.post(
    "",
    summary="Execute Virtual Try-On Pipeline",
    description=(
        "Executes end-to-end AI virtual try-on pipeline. Accepts person and "
        "garment image uploads, validates constraints, and renders fitting."
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "examples": {
                        "upper_body_example": {
                            "summary": "Upper Body Try-On Request",
                            "value": {
                                "garment_category": "upper_body",
                                "engine": "idm_vton",
                                "sync": True,
                            },
                        },
                        "lower_body_example": {
                            "summary": "Lower Body Try-On Request",
                            "value": {
                                "garment_category": "lower_body",
                                "engine": "idm_vton",
                                "sync": True,
                            },
                        },
                        "full_body_example": {
                            "summary": "Full Body Dress Try-On Request",
                            "value": {
                                "garment_category": "full_body",
                                "engine": "idm_vton",
                                "sync": True,
                            },
                        },
                    }
                }
            }
        }
    },
)
async def create_virtual_tryon(
    request: Request,
    person_image: UploadFile = File(
        ..., description="Person photograph file (JPEG, PNG, WebP)"
    ),
    garment_image: UploadFile = File(
        ..., description="Garment image file (JPEG, PNG, WebP)"
    ),
    garment_category: str = Form(
        ..., description="Clothing category: upper_body, lower_body, full_body"
    ),
    engine: Optional[str] = Form(
        default="idm_vton", description="Target try-on engine (default: idm_vton)"
    ),
    sync: bool = Form(
        default=True, description="Synchronous execution mode flag (default: true)"
    ),
    metadata: Optional[str] = Form(
        default=None, description="Optional client JSON metadata string"
    ),
    pipeline: VirtualWearPipeline = Depends(get_virtual_wear_pipeline),
) -> Dict[str, Any]:
    """Handles multipart try-on upload, pipeline execution, and response formatting."""
    t_start = time.perf_counter()
    request_id = getattr(request.state, "request_id", None)
    upload_service = UploadService()

    person_path: Optional[str] = None
    garment_path: Optional[str] = None

    try:
        # 1. Validation & Engine Selection
        t_val_start = time.perf_counter()
        parsed_category = RequestValidator.validate_garment_category(garment_category)
        target_engine = RequestValidator.validate_engine(engine)
        extra_meta = RequestValidator.parse_metadata(metadata)
        t_val_end = time.perf_counter()
        val_duration_ms = (t_val_end - t_val_start) * 1000.0

        # 2. Streaming File Uploads
        t_up_start = time.perf_counter()
        person_path, _, _ = await upload_service.save_uploaded_file(
            person_image, prefix="person"
        )
        garment_path, _, _ = await upload_service.save_uploaded_file(
            garment_image, prefix="garment"
        )
        t_up_end = time.perf_counter()
        upload_duration_ms = (t_up_end - t_up_start) * 1000.0

        # 3. Construct Pipeline Domain Inputs
        person_input = PersonInput(person_id="user_person", image_ref=person_path)
        garment_input = GarmentInput(
            garment_id="user_garment",
            image_ref=garment_path,
            category=parsed_category,
        )

        # 4. Pipeline Execution
        t_pipe_start = time.perf_counter()
        result = await pipeline.run(person_input, garment_input)
        t_pipe_end = time.perf_counter()
        pipe_duration_ms = (t_pipe_end - t_pipe_start) * 1000.0

        t_total_end = time.perf_counter()
        total_duration_ms = (t_total_end - t_start) * 1000.0

        # 5. Response Payload Construction
        response_data = {
            "result_id": result.final.final_image_id,
            "image_ref": result.final.output_ref,
            "engine": target_engine,
            "garment_category": parsed_category.value,
            "sync_mode": sync,
            "engine_metadata": result.pipeline_metadata,
            "timings": {
                "upload_duration_ms": round(upload_duration_ms, 2),
                "validation_duration_ms": round(val_duration_ms, 2),
                "pipeline_duration_ms": round(pipe_duration_ms, 2),
                "total_duration_ms": round(total_duration_ms, 2),
            },
            "client_metadata": extra_meta,
        }

        logger.info(
            f"POST /api/v1/tryon: Rendered '{result.final.final_image_id}' "
            f"in {total_duration_ms:.2f}ms (req_id={request_id})"
        )

        return ResponseBuilder.success(
            data=response_data,
            message="Virtual try-on simulation executed successfully",
            request_id=request_id,
            request_duration_ms=total_duration_ms,
        )

    finally:
        # Automatic File Cleanup: Remove uploaded temporary files after pipeline
        UploadService.cleanup_files(person_path, garment_path)
