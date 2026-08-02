import datetime
import uuid
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Execution states for asynchronous background try-on jobs."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def generate_job_id() -> str:
    """Generates deterministic job ID: job_YYYYMMDD_<8-char-hash>."""
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
    short_hash = uuid.uuid4().hex[:8]
    return f"job_{today_str}_{short_hash}"


class JobResultReference(BaseModel):
    """Lightweight result contract stored inside completed JobModel."""

    result_id: str
    artifact_ref: str
    thumbnail_ref: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    completed_at: str


class JobMetrics(BaseModel):
    """Detailed performance metrics for asynchronous job phases."""

    queue_wait_ms: float = 0.0
    upload_ms: float = 0.0
    validation_ms: float = 0.0
    pipeline_ms: float = 0.0
    cleanup_ms: float = 0.0
    total_ms: float = 0.0


class JobEvent(BaseModel):
    """Structured event log entry tracking job state transitions and progress."""

    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    job_id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    stage: str
    message: str
    progress_percent: int


class JobModel(BaseModel):
    """Complete internal domain representation of a Virtual Try-On job."""

    job_id: str = Field(default_factory=generate_job_id)
    request_id: Optional[str] = None
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: JobStatus = JobStatus.QUEUED
    progress_percent: int = 0
    current_stage: str = "Queued"
    person_path: str
    garment_path: str
    garment_category: str
    engine_name: str = "idm_vton"
    result: Optional[JobResultReference] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    retry_after_seconds: int = 5
    metrics: JobMetrics = Field(default_factory=JobMetrics)


class QueueStatistics(BaseModel):
    """Aggregated queue statistics and job state counts."""

    queue_size: int = 0
    queued_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    cancelled_jobs: int = 0
