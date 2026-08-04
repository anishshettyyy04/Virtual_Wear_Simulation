import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import JSONResponse

from app.api.dependencies.jobs import get_job_manager
from app.api.dependencies.pipeline import get_virtual_wear_pipeline
from app.schemas.ai import GarmentInput, PersonInput
from app.services.ai.pipeline import VirtualWearPipeline
from app.services.api.request_validator import RequestValidator
from app.services.api.response_builder import ResponseBuilder
from app.services.api.upload_service import UploadService
from app.services.jobs.manager import BackgroundJobManager
from app.utils.logger import logger

router = APIRouter(prefix="/tryon", tags=["Virtual Try-On"])


@router.post(
    "",
    summary="Execute Virtual Try-On Pipeline",
    description=(
        "Executes end-to-end AI virtual try-on pipeline. Supports synchronous "
        "or asynchronous background job execution via sync flag."
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "examples": {
                        "sync_example": {
                            "summary": "Synchronous Try-On Request",
                            "value": {
                                "garment_category": "upper_body",
                                "engine": "idm_vton",
                                "sync": True,
                            },
                        },
                        "async_example": {
                            "summary": "Asynchronous Background Try-On Request",
                            "value": {
                                "garment_category": "upper_body",
                                "engine": "idm_vton",
                                "sync": False,
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
        default=True,
        description="Sync flag (default: true, set false for async background job)",
    ),
    metadata: Optional[str] = Form(
        default=None, description="Optional client JSON metadata string"
    ),
    pipeline: VirtualWearPipeline = Depends(get_virtual_wear_pipeline),
    job_manager: BackgroundJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Handles multipart try-on upload and routes to sync or async execution."""
    t_start = time.perf_counter()
    request_id = getattr(request.state, "request_id", None)
    logger.info(
        f"[BACKEND:TRYON:REQUEST] Received request request_id={request_id}, "
        f"person_file={person_image.filename}, garment_file={garment_image.filename}, "
        f"garment_category={garment_category}, engine={engine}, sync={sync}"
    )
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

        # 3. Asynchronous Background Job Submission (sync=false)
        if not sync:
            job = await job_manager.submit_job(
                person_path=person_path,
                garment_path=garment_path,
                garment_category=parsed_category.value,
                engine_name=target_engine,
                request_id=request_id,
                metadata=extra_meta,
            )

            response_data = {
                "job_id": job.job_id,
                "status": job.status.value,
                "progress_percent": job.progress_percent,
                "current_stage": job.current_stage,
                "sync_mode": False,
            }

            payload = ResponseBuilder.success(
                data=response_data,
                message="Try-on request accepted for background processing",
                request_id=request_id,
            )
            return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=payload)

        # 4. Synchronous Pipeline Execution (sync=true)
        person_input = PersonInput(person_id="user_person", image_ref=person_path)
        garment_input = GarmentInput(
            garment_id="user_garment",
            image_ref=garment_path,
            category=parsed_category,
        )

        logger.info("[BACKEND:TRYON:INFERENCE] starting inference")
        t_pipe_start = time.perf_counter()
        result = await pipeline.run(person_input, garment_input)
        t_pipe_end = time.perf_counter()
        logger.info(
            f"[BACKEND:TRYON:INFERENCE_COMPLETE] output_type={type(result).__name__}, "
            f"output_ref={result.final.output_ref}"
        )
        pipe_duration_ms = (t_pipe_end - t_pipe_start) * 1000.0

        t_total_end = time.perf_counter()
        total_duration_ms = (t_total_end - t_start) * 1000.0

        response_data = {
            "result_id": result.final.final_image_id,
            "image_ref": result.final.output_ref,
            "engine": target_engine,
            "garment_category": parsed_category.value,
            "sync_mode": True,
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
        # Automatic File Cleanup: Cleanup upload files for sync execution.

        # For async jobs, BackgroundWorker / JobCleanupService handles file cleanup.
        if sync:

            UploadService.cleanup_files(person_path, garment_path)
