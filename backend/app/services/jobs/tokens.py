import threading
from typing import Optional

from app.services.ai.exceptions import AIPipelineError


class JobCancelledError(AIPipelineError):
    """Exception raised when a background try-on job execution is cancelled."""

    def __init__(
        self,
        message: str = "Job execution was cancelled.",
        job_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.job_id = job_id
        self.reason = reason


class CancellationToken:
    """Thread-safe cancellation token polled periodically by background workers."""

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self._cancelled: bool = False
        self._reason: Optional[str] = None
        self._lock = threading.Lock()

    @property
    def is_cancelled(self) -> bool:
        """Returns boolean indicating if cancellation has been requested."""
        with self._lock:
            return self._cancelled

    @property
    def reason(self) -> Optional[str]:
        """Returns optional cancellation reason string."""
        with self._lock:
            return self._reason

    def cancel(self, reason: str = "User requested cancellation") -> None:
        """Triggers atomic cancellation state."""
        with self._lock:
            self._cancelled = True
            self._reason = reason

    def check_cancelled(self) -> None:
        """Raises JobCancelledError if token has been marked cancelled."""
        if self.is_cancelled:
            raise JobCancelledError(
                message=f"Job '{self.job_id}' was cancelled: {self.reason}",
                job_id=self.job_id,
                reason=self.reason,
            )
