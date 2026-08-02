from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel, Field


class DensePoseResult(BaseModel):
    """Container for DensePose surface estimation result metadata and artifact path."""

    densepose_id: str
    densepose_ref: str
    height: int
    width: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


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
    """Abstract interface for combining multi-modal conditioning for VTON engines."""

    @abstractmethod
    async def prepare(
        self,
        person_image_ref: str,
        garment_image_ref: str,
        agnostic_mask_ref: str,
        **kwargs: Any,
    ) -> Any:
        """Prepares complete conditioning package required by a specific VTON engine."""
        raise NotImplementedError
