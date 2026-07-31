from abc import ABC, abstractmethod

from app.schemas.ai import PoseEstimationResult, PreprocessingResult


class BasePoseEstimator(ABC):
    """Abstract interface defining body posture keypoint estimation stage."""

    @abstractmethod
    async def estimate(self, preprocessed: PreprocessingResult) -> PoseEstimationResult:
        """Extracts skeletal pose landmarks from preprocessed avatar input."""
        pass
