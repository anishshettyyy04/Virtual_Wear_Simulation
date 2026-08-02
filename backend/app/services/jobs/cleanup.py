import asyncio
import datetime
import os
from typing import Dict, Optional, Set

from app.config.settings import Settings, settings
from app.services.api.upload_service import UploadService
from app.services.jobs.models import JobStatus
from app.services.jobs.registry import BaseJobRegistry
from app.utils.logger import logger


class JobCleanupService:
    """Registration-driven cleanup service managing artifact cleanup and job pruning."""

    def __init__(
        self,
        registry: BaseJobRegistry,
        config: Optional[Settings] = None,
    ) -> None:
        self.registry = registry
        self.config = config or settings
        self._running: bool = False
        self._cleanup_task: Optional[asyncio.Task[None]] = None
        self._retention_hours = self.config.AI_JOB_RETENTION_HOURS
        self._cancelled_retention_hours = self.config.AI_CANCELLED_JOB_RETENTION_HOURS
        self._registered_artifacts: Dict[str, Set[str]] = {}

    @property
    def is_running(self) -> bool:
        """Returns boolean indicating if cleanup task is running."""
        return (
            self._running
            and self._cleanup_task is not None
            and not self._cleanup_task.done()
        )

    def register(self, job_id: str, artifact_path: str) -> None:
        """Registers a temporary file or artifact path for cleanup."""
        if job_id not in self._registered_artifacts:
            self._registered_artifacts[job_id] = set()
        self._registered_artifacts[job_id].add(artifact_path)
        logger.debug(
            f"JobCleanupService: Registered '{artifact_path}' for job '{job_id}'"
        )

    def unregister(self, job_id: str) -> None:
        """Unregisters all temporary artifact paths for a job."""
        removed = self._registered_artifacts.pop(job_id, None)
        if removed:
            logger.debug(f"JobCleanupService: Unregistered {len(removed)} artifacts")

    def cleanup(self, job_id: str) -> int:
        """Deletes registered temporary artifacts for a specific job."""
        artifacts = self._registered_artifacts.pop(job_id, set())
        deleted_count = 0
        for path in artifacts:
            try:
                if os.path.exists(path) and os.path.isfile(path):
                    os.remove(path)
                    deleted_count += 1
                    logger.debug(
                        f"JobCleanupService: Removed registered artifact '{path}'"
                    )
            except Exception as exc:
                logger.warning(
                    f"JobCleanupService: Failed to remove artifact '{path}': {exc}"
                )
        return deleted_count

    async def start(self) -> None:
        """Starts periodic cleanup task."""
        if self._running:
            return
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("JobCleanupService: Periodic retention cleanup task started.")

    async def shutdown(self) -> None:
        """Stops periodic cleanup task."""
        self._running = False
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("JobCleanupService: Periodic cleanup task stopped.")

    async def _cleanup_loop(self) -> None:
        """Loops periodically pruning expired jobs every 15 minutes."""
        while self._running:
            try:
                self.prune_expired_jobs()
                await asyncio.sleep(900)  # Check every 15 minutes
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"JobCleanupService: Cleanup loop error: {exc}")
                await asyncio.sleep(60)

    def prune_expired_jobs(self) -> int:
        """Prunes expired completed, failed, and cancelled jobs."""
        now = datetime.datetime.now(datetime.timezone.utc)
        all_jobs = self.registry.list_jobs(limit=1000)
        pruned_count = 0

        for job in all_jobs:
            if not job.completed_at:
                continue

            try:
                comp_dt = datetime.datetime.fromisoformat(job.completed_at)
                age_hours = (now - comp_dt).total_seconds() / 3600.0

                should_prune = False
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                    if age_hours >= self._retention_hours:
                        should_prune = True
                elif job.status == JobStatus.CANCELLED:
                    if age_hours >= self._cancelled_retention_hours:
                        should_prune = True

                if should_prune:
                    # Clean up temporary registered artifacts
                    self.cleanup(job.job_id)
                    # Clean up input upload files (person_path, garment_path)
                    UploadService.cleanup_files(job.person_path, job.garment_path)
                    pruned_count += 1
                    logger.info(f"JobCleanupService: Pruned expired job '{job.job_id}'")

            except Exception as exc:
                logger.warning(
                    f"JobCleanupService: Error evaluating job '{job.job_id}': {exc}"
                )

        return pruned_count
