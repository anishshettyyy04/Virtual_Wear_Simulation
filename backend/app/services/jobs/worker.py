import asyncio
import datetime
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Dict, Optional

from app.config.settings import settings
from app.schemas.ai import GarmentCategory, GarmentInput, PersonInput
from app.services.ai.pipeline import VirtualWearPipeline
from app.services.jobs.lifecycle import JobLifecycle
from app.services.jobs.models import (
    JobMetrics,
    JobModel,
    JobResultReference,
    JobStatus,
)
from app.services.jobs.queue import BaseJobQueue
from app.services.jobs.registry import BaseJobRegistry
from app.services.jobs.tokens import CancellationToken, JobCancelledError
from app.utils.logger import logger


class WorkerState(str, Enum):
    """Lifecycle state machine for background worker workers."""

    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"


class BaseWorker(ABC):
    """Abstract Base Class defining worker lifecycle interface."""

    @property
    @abstractmethod
    def state(self) -> WorkerState:
        """Returns current lifecycle state of worker."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initializes worker resources."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Starts worker loop listening for jobs."""
        pass

    @abstractmethod
    async def pause(self) -> None:
        """Pauses worker execution loop."""
        pass

    @abstractmethod
    async def resume(self) -> None:
        """Resumes worker execution loop."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully shuts down worker resources."""
        pass


class BackgroundWorker(BaseWorker):
    """Worker consuming job queue items and driving pipeline execution."""

    def __init__(
        self,
        queue: BaseJobQueue,
        registry: BaseJobRegistry,
        pipeline_factory: Callable[[], VirtualWearPipeline],
    ) -> None:
        self.queue = queue
        self.registry = registry
        self.pipeline_factory = pipeline_factory
        self.lifecycle = JobLifecycle()
        self._state: WorkerState = WorkerState.STOPPED
        self._worker_task: Optional[asyncio.Task[None]] = None
        self._active_tokens: Dict[str, CancellationToken] = {}

    @property
    def state(self) -> WorkerState:
        """Returns current worker lifecycle state."""
        return self._state

    async def initialize(self) -> None:
        """Worker initialization pass."""
        self._state = WorkerState.INITIALIZING
        logger.info("BackgroundWorker: Initializing worker...")

    async def start(self) -> None:
        """Launches worker loop background task."""
        if self._state == WorkerState.RUNNING:
            return
        self._state = WorkerState.RUNNING
        self._worker_task = asyncio.create_task(self._run_loop())
        logger.info("BackgroundWorker: Worker loop started.")

    async def pause(self) -> None:
        """Pauses worker loop processing."""
        if self._state == WorkerState.RUNNING:
            self._state = WorkerState.PAUSED
            logger.info("BackgroundWorker: Worker loop paused.")

    async def resume(self) -> None:
        """Resumes worker loop processing."""
        if self._state == WorkerState.PAUSED:
            self._state = WorkerState.RUNNING
            logger.info("BackgroundWorker: Worker loop resumed.")

    async def shutdown(self) -> None:
        """Gracefully shuts down worker background task cleanly."""
        if self._state in (WorkerState.STOPPING, WorkerState.STOPPED):
            return

        self._state = WorkerState.STOPPING
        logger.info("BackgroundWorker: Worker gracefully shutting down...")

        # Cancel active tokens
        for token in list(self._active_tokens.values()):
            token.cancel("Worker shutdown requested")

        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        self._state = WorkerState.STOPPED
        logger.info("BackgroundWorker: Worker loop shut down successfully.")

    def get_cancellation_token(self, job_id: str) -> CancellationToken:
        """Creates and registers a CancellationToken for a job."""
        token = self._active_tokens.get(job_id)
        if token is None:
            token = CancellationToken(job_id)
            self._active_tokens[job_id] = token
        return token

    async def _run_loop(self) -> None:
        """Continuous consumer loop dequeuing and processing jobs."""
        poll_interval_sec = settings.AI_WORKER_POLL_INTERVAL_MS / 1000.0

        while self._state in (WorkerState.RUNNING, WorkerState.PAUSED):
            try:
                if self._state == WorkerState.PAUSED or self.queue.empty():
                    await asyncio.sleep(poll_interval_sec)
                    continue

                job = await self.queue.get()
                if job is None:
                    continue

                await self._process_job(job)

            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(
                    f"BackgroundWorker: Worker loop error: {exc}", exc_info=True
                )
                await asyncio.sleep(0.5)

    def _emit_stage_progress(self, job: JobModel, stage: str, message: str) -> None:
        """Updates job model stage/progress via JobLifecycle."""
        self.lifecycle.transition(
            job=job,
            new_status=job.status,
            stage=stage,
            message=message,
            registry=self.registry,
        )

    def _handle_cancellation(self, job: JobModel, reason: str) -> None:
        """Updates job model state to CANCELLED via JobLifecycle."""
        self.lifecycle.transition(
            job=job,
            new_status=JobStatus.CANCELLED,
            stage="Cancelled",
            message=f"Job cancelled: {reason}",
            error=f"Job cancelled: {reason}",
            registry=self.registry,
        )
        self._active_tokens.pop(job.job_id, None)

    async def _process_job(self, job: JobModel) -> None:
        """Executes AI try-on pipeline for a single dequeued job."""
        token = self.get_cancellation_token(job.job_id)
        t_job_start = time.perf_counter()

        if token.is_cancelled:
            self._handle_cancellation(
                job, token.reason or "Cancelled prior to execution"
            )
            return

        # 1. Transition state to RUNNING
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.lifecycle.transition(
            job=job,
            new_status=JobStatus.RUNNING,
            stage="Preprocessing",
            message="Started pre-pipeline initialization",
            registry=self.registry,
        )

        try:
            token.check_cancelled()

            # Calculate Queue Wait
            created_dt = datetime.datetime.fromisoformat(job.created_at)
            now_dt = datetime.datetime.fromisoformat(now_iso)
            queue_wait_ms = (now_dt - created_dt).total_seconds() * 1000.0

            # 2. Build Pipeline Inputs
            person_input = PersonInput(
                person_id="job_person", image_ref=job.person_path
            )
            garment_input = GarmentInput(
                garment_id="job_garment",
                image_ref=job.garment_path,
                category=GarmentCategory(job.garment_category),
            )

            token.check_cancelled()
            self._emit_stage_progress(
                job, "Human Parsing", "Running human body parsing"
            )

            pipeline = self.pipeline_factory()

            token.check_cancelled()
            self._emit_stage_progress(
                job, "Pose Estimation", "Estimating skeletal keypoints"
            )

            token.check_cancelled()
            self._emit_stage_progress(
                job, "Agnostic Mask", "Generating agnostic clothing mask"
            )

            token.check_cancelled()
            self._emit_stage_progress(
                job, "Conditioning", "Preparing conditioning bundle"
            )

            token.check_cancelled()
            self._emit_stage_progress(
                job, "Try-On", "Executing neural virtual try-on engine"
            )

            t_pipe_start = time.perf_counter()
            result = await pipeline.run(person_input, garment_input)
            t_pipe_end = time.perf_counter()
            pipe_duration_ms = (t_pipe_end - t_pipe_start) * 1000.0

            token.check_cancelled()
            self._emit_stage_progress(job, "Postprocessing", "Finalizing try-on render")

            t_job_end = time.perf_counter()
            total_duration_ms = (t_job_end - t_job_start) * 1000.0

            # 3. Construct Result Reference
            done_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            result_ref = JobResultReference(
                result_id=result.final.final_image_id,
                artifact_ref=result.final.output_ref,
                completed_at=done_iso,
                metadata=result.pipeline_metadata,
            )

            metrics = JobMetrics(
                queue_wait_ms=round(queue_wait_ms, 2),
                pipeline_ms=round(pipe_duration_ms, 2),
                total_ms=round(total_duration_ms, 2),
            )
            job.metrics = metrics

            self.lifecycle.transition(
                job=job,
                new_status=JobStatus.COMPLETED,
                stage="Completed",
                message="Job executed successfully",
                result=result_ref,
                registry=self.registry,
            )
            logger.info(
                f"BackgroundWorker: Completed job '{job.job_id}' in "
                f"{total_duration_ms:.2f}ms"
            )

        except JobCancelledError as exc:
            logger.warning(f"BackgroundWorker: Job '{job.job_id}' cancelled: {exc}")
            self._handle_cancellation(job, exc.reason or "Execution cancelled")

        except Exception as exc:
            logger.error(
                f"BackgroundWorker: Job '{job.job_id}' failed: {exc}",
                exc_info=True,
            )
            self.lifecycle.transition(
                job=job,
                new_status=JobStatus.FAILED,
                stage="Failed",
                message=f"Job failed: {exc}",
                error=str(exc),
                registry=self.registry,
            )

        finally:
            self._active_tokens.pop(job.job_id, None)
