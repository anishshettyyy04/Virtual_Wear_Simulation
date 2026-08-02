import asyncio
from abc import ABC, abstractmethod

from app.services.jobs.models import JobModel
from app.utils.logger import logger


class BaseJobQueue(ABC):
    """Abstract Base Class for Virtual Try-On job queues."""

    @abstractmethod
    async def put(self, job: JobModel) -> None:
        """Enqueues a job item into the queue."""
        pass

    @abstractmethod
    async def get(self) -> JobModel:
        """Dequeues and returns the next job item."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Returns current number of queued items."""
        pass

    @abstractmethod
    def empty(self) -> bool:
        """Returns True if the queue contains no items."""
        pass

    @abstractmethod
    def cancel(self, job_id: str) -> bool:
        """Attempts to cancel a queued job item before worker consumption."""
        pass


class InMemoryJobQueue(BaseJobQueue):
    """In-memory asyncio.Queue FIFO job queue implementation."""

    def __init__(self, maxsize: int = 100) -> None:
        self.maxsize = maxsize
        self._queue: asyncio.Queue[JobModel] = asyncio.Queue(maxsize=maxsize)
        self._pending_ids: set[str] = set()

    async def put(self, job: JobModel) -> None:
        """Enqueues a job into the queue."""
        await self._queue.put(job)
        self._pending_ids.add(job.job_id)
        logger.info(
            f"InMemoryJobQueue: Enqueued job '{job.job_id}' (qsize={self.size()})"
        )

    async def get(self) -> JobModel:
        """Dequeues the next job."""
        job = await self._queue.get()
        self._pending_ids.discard(job.job_id)
        return job

    def size(self) -> int:
        """Returns number of items in queue."""
        return self._queue.qsize()

    def empty(self) -> bool:
        """Returns boolean indicating if queue is empty."""
        return self._queue.empty()

    def cancel(self, job_id: str) -> bool:
        """Removes job_id from pending set if still queued."""
        if job_id in self._pending_ids:
            self._pending_ids.discard(job_id)
            logger.info(f"InMemoryJobQueue: Marked queued job '{job_id}' cancelled")
            return True
        return False
