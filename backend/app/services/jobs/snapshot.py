from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.services.jobs.models import (
    JobMetrics,
    JobModel,
    JobResultReference,
    JobStatus,
)


class JobSnapshot(BaseModel):
    """Immutable snapshot representation of a job for API responses."""

    job_id: str
    request_id: Optional[str] = None
    status: JobStatus
    progress_percent: int
    current_stage: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[JobResultReference] = None
    error: Optional[str] = None
    metrics: JobMetrics = Field(default_factory=JobMetrics)
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_job(cls, job: JobModel) -> "JobSnapshot":
        """Constructs an immutable snapshot from a JobModel instance."""
        return cls(
            job_id=job.job_id,
            request_id=job.request_id,
            status=job.status,
            progress_percent=job.progress_percent,
            current_stage=job.current_stage,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            result=job.result,
            error=job.error,
            metrics=job.metrics,
            retry_count=job.retry_count,
            metadata=job.metadata,
        )
