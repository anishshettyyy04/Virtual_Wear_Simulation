from typing import Any, Callable, Dict, List, Optional

from app.services.ai.pipeline import VirtualWearPipeline
from app.services.jobs.cleanup import JobCleanupService
from app.services.jobs.lifecycle import JobLifecycle
from app.services.jobs.models import (
    JobEvent,
    JobModel,
    JobStatus,
    QueueStatistics,
    generate_job_id,
)
from app.services.jobs.queue import BaseJobQueue, InMemoryJobQueue
from app.services.jobs.registry import BaseJobRegistry, MemoryJobRegistry
from app.services.jobs.snapshot import JobSnapshot
from app.services.jobs.worker import BackgroundWorker
from app.utils.logger import logger


class BackgroundJobManager:
    """Orchestrator managing job submission, queueing, worker, and status querying."""

    def __init__(
        self,
        queue: Optional[BaseJobQueue] = None,
        registry: Optional[BaseJobRegistry] = None,
        pipeline_factory: Optional[Callable[[], VirtualWearPipeline]] = None,
    ) -> None:
        self.queue = queue or InMemoryJobQueue()
        self.registry = registry or MemoryJobRegistry()

        if pipeline_factory is None:
            from app.api.dependencies.pipeline import get_virtual_wear_pipeline

            pipeline_factory = get_virtual_wear_pipeline

        self.worker = BackgroundWorker(
            queue=self.queue,
            registry=self.registry,
            pipeline_factory=pipeline_factory,
        )
        self.cleanup_service = JobCleanupService(registry=self.registry)
        self.lifecycle = JobLifecycle()

    async def start(self) -> None:
        """Starts worker and cleanup background loops."""
        await self.worker.initialize()
        await self.worker.start()
        await self.cleanup_service.start()
        logger.info("BackgroundJobManager: Job manager started.")

    async def shutdown(self) -> None:
        """Shuts down worker and cleanup tasks cleanly."""
        await self.worker.shutdown()
        await self.cleanup_service.shutdown()
        logger.info("BackgroundJobManager: Job manager shut down.")

    async def submit_job(
        self,
        person_path: str,
        garment_path: str,
        garment_category: str,
        engine_name: str = "idm_vton",
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobModel:
        """Constructs a new JobModel, registers it, and enqueues it."""
        job = JobModel(
            job_id=generate_job_id(),
            request_id=request_id,
            person_path=person_path,
            garment_path=garment_path,
            garment_category=garment_category,
            engine_name=engine_name,
            metadata=metadata or {},
        )

        self.registry.add(job)
        # Register uploaded input files for cleanup
        self.cleanup_service.register(job.job_id, person_path)
        self.cleanup_service.register(job.job_id, garment_path)

        await self.queue.put(job)
        logger.info(f"BackgroundJobManager: Submitted job '{job.job_id}'")
        return job

    def get_job(self, job_id: str) -> Optional[JobModel]:
        """Retrieves internal job model by ID."""
        return self.registry.get(job_id)

    def get_snapshot(self, job_id: str) -> Optional[JobSnapshot]:
        """Retrieves immutable JobSnapshot for REST API serialization."""
        job = self.registry.get(job_id)
        if not job:
            return None
        return JobSnapshot.from_job(job)

    def get_job_events(self, job_id: str) -> List[JobEvent]:
        """Retrieves event timeline for a given job_id."""
        return self.registry.get_events(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancels a queued or running job via JobLifecycle."""
        job = self.registry.get(job_id)
        if not job:
            return False

        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            return False

        # Attempt queue cancellation if still queued
        cancelled_in_queue = self.queue.cancel(job_id)

        # Trigger worker cancellation token if running
        token = self.worker.get_cancellation_token(job_id)
        token.cancel("Cancelled via API request")

        self.lifecycle.transition(
            job=job,
            new_status=JobStatus.CANCELLED,
            stage="Cancelled",
            message="Job cancelled via API request",
            error="Job cancelled via API request",
            registry=self.registry,
        )

        logger.info(
            f"BackgroundJobManager: Cancelled job '{job_id}' "
            f"(in_queue={cancelled_in_queue})"
        )
        return True

    def get_statistics(self) -> QueueStatistics:
        """Calculates aggregated queue statistics and job counts."""
        all_jobs = self.registry.list_jobs(limit=5000)
        return QueueStatistics(
            queue_size=self.queue.size(),
            queued_jobs=sum(1 for j in all_jobs if j.status == JobStatus.QUEUED),
            running_jobs=sum(1 for j in all_jobs if j.status == JobStatus.RUNNING),
            completed_jobs=sum(1 for j in all_jobs if j.status == JobStatus.COMPLETED),
            failed_jobs=sum(1 for j in all_jobs if j.status == JobStatus.FAILED),
            cancelled_jobs=sum(1 for j in all_jobs if j.status == JobStatus.CANCELLED),
        )

    def get_health(self) -> Dict[str, Any]:
        """Returns background job manager health and metrics for health API."""
        stats = self.get_statistics()
        return {
            "worker_state": self.worker.state.value,
            "queue_size": stats.queue_size,
            "active_jobs": stats.queued_jobs + stats.running_jobs,
            "completed_jobs": stats.completed_jobs,
            "failed_jobs": stats.failed_jobs,
            "cancelled_jobs": stats.cancelled_jobs,
            "cleanup_service": (
                "running" if self.cleanup_service.is_running else "stopped"
            ),
        }
