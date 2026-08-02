from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies.jobs import get_job_manager
from app.services.api.response_builder import ErrorCode, ResponseBuilder
from app.services.jobs.manager import BackgroundJobManager
from app.services.jobs.models import JobStatus

router = APIRouter(prefix="/jobs", tags=["Background Jobs"])


@router.get(
    "/{job_id}",
    summary="Get Job Status & Progress",
    description="Inspects real-time progress, stage, timestamps, and metrics.",
)
async def get_job_status(
    job_id: str,
    request: Request,
    job_manager: BackgroundJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Returns current status, progress percentage, stage, and timestamps for a job."""
    snapshot = job_manager.get_snapshot(job_id)
    request_id = getattr(request.state, "request_id", None)

    if not snapshot:
        return ResponseBuilder.error(
            code="NOT_FOUND",
            message=f"Job '{job_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            request_id=request_id,
        )

    return ResponseBuilder.success(
        data=snapshot.model_dump(),
        message=f"Job '{job_id}' status retrieved successfully",
        request_id=request_id,
    )


@router.get(
    "/{job_id}/result",
    summary="Get Job Render Result",
    description="Retrieves the final rendered try-on result once execution completes.",
)
async def get_job_result(
    job_id: str,
    request: Request,
    job_manager: BackgroundJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Returns result reference payload if completed, or error if processing/failed."""
    snapshot = job_manager.get_snapshot(job_id)
    request_id = getattr(request.state, "request_id", None)

    if not snapshot:
        return ResponseBuilder.error(
            code="NOT_FOUND",
            message=f"Job '{job_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            request_id=request_id,
        )

    if snapshot.status in (JobStatus.RUNNING, JobStatus.QUEUED):
        return ResponseBuilder.error(
            code="JOB_IN_PROGRESS",
            message=(
                f"Job '{job_id}' is still processing (stage: {snapshot.current_stage}, "
                f"progress: {snapshot.progress_percent}%)."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
        )

    if snapshot.status == JobStatus.FAILED:
        return ResponseBuilder.error(
            code=ErrorCode.PIPELINE_FAILED,
            message=f"Job '{job_id}' failed during execution: {snapshot.error}",
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
        )

    if snapshot.status == JobStatus.CANCELLED:
        return ResponseBuilder.error(
            code="JOB_CANCELLED",
            message=f"Job '{job_id}' was cancelled.",
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
        )

    if not snapshot.result:
        return ResponseBuilder.error(
            code="RESULT_NOT_AVAILABLE",
            message=f"Result artifact for job '{job_id}' is unavailable.",
            status_code=status.HTTP_404_NOT_FOUND,
            request_id=request_id,
        )

    return ResponseBuilder.success(
        data=snapshot.result.model_dump(),
        message=f"Result for job '{job_id}' retrieved successfully",
        request_id=request_id,
    )


@router.delete(
    "/{job_id}",
    summary="Cancel Job Execution",
    description="Cancels a pending or running try-on job and releases resources.",
)
async def cancel_job(
    job_id: str,
    request: Request,
    job_manager: BackgroundJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Cancels a pending or running job."""
    request_id = getattr(request.state, "request_id", None)
    success = job_manager.cancel_job(job_id)

    if not success:
        snapshot = job_manager.get_snapshot(job_id)
        if not snapshot:
            return ResponseBuilder.error(
                code="NOT_FOUND",
                message=f"Job '{job_id}' not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                request_id=request_id,
            )
        return ResponseBuilder.error(
            code="JOB_NOT_CANCELLABLE",
            message=(
                f"Job '{job_id}' cannot be cancelled (status: {snapshot.status.value})."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
        )

    return ResponseBuilder.success(
        data={"job_id": job_id, "status": "cancelled"},
        message=f"Job '{job_id}' cancelled successfully",
        request_id=request_id,
    )
