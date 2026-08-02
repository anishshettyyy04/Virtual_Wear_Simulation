from abc import ABC, abstractmethod
from typing import Any, Optional

from app.schemas.ai import (
    AgnosticMaskResult,
    ConditioningBundle,
    DensePoseResult,
    GarmentInput,
    HumanParsingResult,
    PoseEstimationResult,
    PreprocessingResult,
)


class BaseDensePoseService(ABC):
    """Abstract interface for DensePose body surface estimation service."""

    @abstractmethod
    async def process(self, person_image_ref: str) -> DensePoseResult:
        """Generates DensePose IUV surface map from preprocessed person image."""
        raise NotImplementedError


class BaseImageAdapter(ABC):
    """Abstract interface for VTON model image resolution adaptation."""

    @abstractmethod
    def adapt(self, image_ref: str, target_width: int, target_height: int) -> Any:
        """Adapts input image artifact to target resolution required by VTON engine."""
        raise NotImplementedError


class BaseMaskAdapter(ABC):
    """Abstract interface for VTON model mask format and tensor conversion."""

    @abstractmethod
    def adapt(self, mask_ref: str, target_width: int, target_height: int) -> Any:
        """Adapts canonical agnostic mask artifact to target format for VTON engine."""
        raise NotImplementedError


class BaseConditioningAdapter(ABC):
    """Abstract interface for producing a ConditioningBundle."""

    @abstractmethod
    async def prepare(
        self,
        preprocessed: PreprocessingResult,
        parsing: HumanParsingResult,
        pose: PoseEstimationResult,
        agnostic_mask: AgnosticMaskResult,
        garment: GarmentInput,
        densepose: Optional[DensePoseResult] = None,
        **kwargs: Any,
    ) -> ConditioningBundle:
        """Prepares canonical ConditioningBundle for try-on engines."""
        raise NotImplementedError
