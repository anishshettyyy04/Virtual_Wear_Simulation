import datetime
from typing import Optional

from app.services.jobs.models import (
    JobEvent,
    JobModel,
    JobResultReference,
    JobStatus,
)
from app.services.jobs.progress import ProgressTracker
from app.services.jobs.registry import BaseJobRegistry


class JobLifecycle:
    """Centralized lifecycle manager governing job state transitions and events."""

    def __init__(
        self,
        progress_tracker: Optional[ProgressTracker] = None,
    ) -> None:
        self.progress_tracker = progress_tracker or ProgressTracker()

    def transition(
        self,
        job: JobModel,
        new_status: JobStatus,
        stage: Optional[str] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        result: Optional[JobResultReference] = None,
        registry: Optional[BaseJobRegistry] = None,
    ) -> JobModel:
        """Transitions job to new state, updating timestamps and emitting events."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        job.status = new_status

        if new_status == JobStatus.RUNNING and not job.started_at:
            job.started_at = now_iso

        if new_status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            job.completed_at = now_iso

        if error is not None:
            job.error = error

        if result is not None:
            job.result = result

        if stage is not None:
            job.current_stage = stage
            job.progress_percent = self.progress_tracker.get_progress_percent(stage)
        elif new_status == JobStatus.COMPLETED:
            job.current_stage = "Completed"
            job.progress_percent = 100

        if registry is not None:
            registry.update(job)
            event_stage = stage or job.current_stage
            event_msg = message or f"Job status changed to {new_status.value}"
            event = JobEvent(
                job_id=job.job_id,
                stage=event_stage,
                message=event_msg,
                progress_percent=job.progress_percent,
            )
            registry.add_event(event)

        return job
