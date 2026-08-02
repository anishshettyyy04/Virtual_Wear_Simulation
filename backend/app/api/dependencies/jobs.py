from typing import Optional

from app.services.jobs.manager import BackgroundJobManager

_job_manager_instance: Optional[BackgroundJobManager] = None


def get_job_manager() -> BackgroundJobManager:
    """Dependency provider returning singleton BackgroundJobManager instance."""
    global _job_manager_instance
    if _job_manager_instance is None:
        _job_manager_instance = BackgroundJobManager()
    return _job_manager_instance
