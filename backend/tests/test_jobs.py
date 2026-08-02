import asyncio
import os
import tempfile

import pytest

from app.services.jobs import (
    BackgroundJobManager,
    BackgroundWorker,
    InMemoryJobQueue,
    JobCleanupService,
    JobLifecycle,
    JobModel,
    JobSnapshot,
    JobStatus,
    MemoryJobRegistry,
    ProgressTracker,
    QueueStatistics,
    WorkerState,
    generate_job_id,
)


@pytest.mark.asyncio
async def test_deterministic_job_id():
    """Verifies deterministic job ID format: job_YYYYMMDD_<8-char-hash>."""
    job_id = generate_job_id()
    assert job_id.startswith("job_")
    parts = job_id.split("_")
    assert len(parts) == 3
    assert len(parts[1]) == 8  # YYYYMMDD
    assert len(parts[2]) == 8  # hex hash


@pytest.mark.asyncio
async def test_job_snapshot_serialization():
    """Verifies JobSnapshot immutability and from_job factory method."""
    job = JobModel(
        person_path="/tmp/person.jpg",
        garment_path="/tmp/garment.jpg",
        garment_category="upper_body",
    )
    job.progress_percent = 45
    job.current_stage = "Human Parsing"

    snapshot = JobSnapshot.from_job(job)
    assert snapshot.job_id == job.job_id
    assert snapshot.status == JobStatus.QUEUED
    assert snapshot.progress_percent == 45
    assert snapshot.current_stage == "Human Parsing"

    dump = snapshot.model_dump()
    assert dump["job_id"] == job.job_id
    assert dump["status"] == "queued"


@pytest.mark.asyncio
async def test_progress_tracker_profile():
    """Verifies ProgressTracker cumulative stage weights."""
    tracker = ProgressTracker()
    assert tracker.get_progress_percent("Queued") == 0
    assert tracker.get_progress_percent("Completed") == 100
    assert tracker.get_progress_percent("Preprocessing") > 0
    assert tracker.get_progress_percent("Try-On") > tracker.get_progress_percent(
        "Conditioning"
    )


@pytest.mark.asyncio
async def test_job_lifecycle_transitions():
    """Verifies JobLifecycle transitions state, timestamps, and progress."""
    registry = MemoryJobRegistry()
    lifecycle = JobLifecycle()
    job = JobModel(
        person_path="/tmp/p.jpg",
        garment_path="/tmp/g.jpg",
        garment_category="upper_body",
    )
    registry.add(job)

    # Transition to RUNNING
    lifecycle.transition(
        job,
        JobStatus.RUNNING,
        stage="Preprocessing",
        message="Preprocessing started",
        registry=registry,
    )
    assert job.status == JobStatus.RUNNING
    assert job.started_at is not None
    assert job.current_stage == "Preprocessing"

    # Transition to COMPLETED
    lifecycle.transition(
        job,
        JobStatus.COMPLETED,
        stage="Completed",
        message="Done",
        registry=registry,
    )
    assert job.status == JobStatus.COMPLETED
    assert job.completed_at is not None
    assert job.progress_percent == 100

    events = registry.get_events(job.job_id)
    assert len(events) == 2
    assert events[0].stage == "Preprocessing"
    assert events[1].stage == "Completed"


@pytest.mark.asyncio
async def test_concurrent_registry_updates():
    """Verifies concurrency safety of MemoryJobRegistry under concurrent operations."""
    registry = MemoryJobRegistry()
    jobs = [
        JobModel(
            person_path=f"/tmp/p_{i}.jpg",
            garment_path=f"/tmp/g_{i}.jpg",
            garment_category="upper_body",
        )
        for i in range(20)
    ]

    async def register_job(j: JobModel):
        await registry.add_async(j)

    await asyncio.gather(*(register_job(j) for j in jobs))
    listed = registry.list_jobs(limit=100)
    assert len(listed) == 20


@pytest.mark.asyncio
async def test_worker_lifecycle_and_pause_resume():
    """Verifies WorkerState state transitions (INITIALIZING, RUNNING, PAUSED, etc.)."""
    queue = InMemoryJobQueue()
    registry = MemoryJobRegistry()
    worker = BackgroundWorker(
        queue=queue,
        registry=registry,
        pipeline_factory=lambda: None,
    )

    assert worker.state == WorkerState.STOPPED

    await worker.initialize()
    assert worker.state == WorkerState.INITIALIZING

    await worker.start()
    assert worker.state == WorkerState.RUNNING

    await worker.pause()
    assert worker.state == WorkerState.PAUSED

    await worker.resume()
    assert worker.state == WorkerState.RUNNING

    await worker.shutdown()
    assert worker.state == WorkerState.STOPPED


@pytest.mark.asyncio
async def test_cleanup_registration_and_execution():
    """Verifies JobCleanupService register, unregister, and cleanup functionality."""
    registry = MemoryJobRegistry()
    cleanup_service = JobCleanupService(registry=registry)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        job_id = "test_job_123"
        cleanup_service.register(job_id, tmp_path)
        assert os.path.exists(tmp_path)

        deleted = cleanup_service.cleanup(job_id)
        assert deleted == 1
        assert not os.path.exists(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@pytest.mark.asyncio
async def test_job_manager_statistics_and_health():
    """Verifies QueueStatistics and get_health output from BackgroundJobManager."""
    manager = BackgroundJobManager()
    await manager.start()

    try:
        health = manager.get_health()
        assert health["worker_state"] == "running"
        assert health["queue_size"] == 0
        assert health["active_jobs"] == 0
        assert health["cleanup_service"] == "running"

        stats = manager.get_statistics()
        assert isinstance(stats, QueueStatistics)
        assert stats.queued_jobs == 0
    finally:
        await manager.shutdown()


@pytest.mark.asyncio
async def test_job_submission_and_cancellation():
    """Verifies async job submission & cancellation via BackgroundJobManager."""

    manager = BackgroundJobManager()
    await manager.start()

    try:
        job = await manager.submit_job(
            person_path="data/test_person.jpg",
            garment_path="data/test_garment.jpg",
            garment_category="upper_body",
        )

        assert job.status in (JobStatus.QUEUED, JobStatus.RUNNING)
        snapshot = manager.get_snapshot(job.job_id)
        assert snapshot is not None
        assert snapshot.job_id == job.job_id

        cancelled = manager.cancel_job(job.job_id)
        assert cancelled is True
        updated_snapshot = manager.get_snapshot(job.job_id)
        assert updated_snapshot.status == JobStatus.CANCELLED
    finally:
        await manager.shutdown()
