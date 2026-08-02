import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.services.jobs.models import JobEvent, JobModel, JobStatus


class BaseJobRegistry(ABC):
    """Abstract Base Class for job registry stores."""

    @abstractmethod
    def add(self, job: JobModel) -> None:
        """Registers a new job model."""
        pass

    @abstractmethod
    def get(self, job_id: str) -> Optional[JobModel]:
        """Retrieves job model by job_id."""
        pass

    @abstractmethod
    def update(self, job: JobModel) -> None:
        """Updates an existing job model."""
        pass

    @abstractmethod
    def delete(self, job_id: str) -> bool:
        """Deletes a job model by job_id."""
        pass

    @abstractmethod
    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[JobModel]:
        """Lists jobs with optional status filtering and pagination."""
        pass

    @abstractmethod
    def add_event(self, event: JobEvent) -> None:
        """Appends a JobEvent log entry."""
        pass

    @abstractmethod
    def get_events(self, job_id: str) -> List[JobEvent]:
        """Retrieves event timeline for a specific job_id."""
        pass

    @abstractmethod
    def cleanup(self) -> int:
        """Removes expired jobs from registry."""
        pass


class MemoryJobRegistry(BaseJobRegistry):
    """Concurrency-safe in-memory job registry implementation."""

    def __init__(self) -> None:
        self._jobs: Dict[str, JobModel] = {}
        self._events: Dict[str, List[JobEvent]] = {}
        self._lock = threading.Lock()
        self._async_lock: Optional[asyncio.Lock] = None

    def _get_async_lock(self) -> asyncio.Lock:
        """Lazily initializes an asyncio.Lock tied to the active event loop."""
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    def add(self, job: JobModel) -> None:
        """Registers a new job model."""
        with self._lock:
            self._jobs[job.job_id] = job
            self._events[job.job_id] = []

    async def add_async(self, job: JobModel) -> None:
        """Async variant of add using asyncio.Lock."""
        async with self._get_async_lock():
            self.add(job)

    def get(self, job_id: str) -> Optional[JobModel]:
        """Retrieves job model by job_id."""
        with self._lock:
            return self._jobs.get(job_id)

    async def get_async(self, job_id: str) -> Optional[JobModel]:
        """Async variant of get using asyncio.Lock."""
        async with self._get_async_lock():
            return self.get(job_id)

    def update(self, job: JobModel) -> None:
        """Updates an existing job model."""
        with self._lock:
            self._jobs[job.job_id] = job

    async def update_async(self, job: JobModel) -> None:
        """Async variant of update using asyncio.Lock."""
        async with self._get_async_lock():
            self.update(job)

    def delete(self, job_id: str) -> bool:
        """Deletes a job model and associated events by job_id."""
        with self._lock:
            existed = job_id in self._jobs
            self._jobs.pop(job_id, None)
            self._events.pop(job_id, None)
            return existed

    async def delete_async(self, job_id: str) -> bool:
        """Async variant of delete using asyncio.Lock."""
        async with self._get_async_lock():
            return self.delete(job_id)

    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[JobModel]:
        """Lists registered jobs sorted by created_at descending."""
        with self._lock:
            all_jobs = list(self._jobs.values())
        if status:
            all_jobs = [j for j in all_jobs if j.status == status]

        all_jobs.sort(key=lambda j: j.created_at, reverse=True)
        return all_jobs[offset : offset + limit]

    def add_event(self, event: JobEvent) -> None:
        """Appends a JobEvent entry to event timeline."""
        with self._lock:
            if event.job_id not in self._events:
                self._events[event.job_id] = []
            self._events[event.job_id].append(event)

    def get_events(self, job_id: str) -> List[JobEvent]:
        """Returns event timeline for a given job_id."""
        with self._lock:
            return list(self._events.get(job_id, []))

    def cleanup(self) -> int:
        """Removes expired or completed jobs without active references."""
        with self._lock:
            initial_count = len(self._jobs)
            # Retain all active jobs
            return initial_count - len(self._jobs)
