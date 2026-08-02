from abc import ABC, abstractmethod
from typing import Optional

from app.schemas.ai import (
    AgnosticMaskResult,
    ConditioningBundle,
    GarmentInput,
    HumanParsingResult,
    PoseEstimationResult,
    PreprocessingResult,
    RawTryOnOutput,
)


class BaseTryOnEngine(ABC):
    """Model-agnostic abstract interface defining virtual try-on neural engine stage."""

    @abstractmethod
    async def generate(
        self,
        preprocessed: Optional[PreprocessingResult] = None,
        parsing: Optional[HumanParsingResult] = None,
        pose: Optional[PoseEstimationResult] = None,
        agnostic_mask: Optional[AgnosticMaskResult] = None,
        garment: Optional[GarmentInput] = None,
        conditioning: Optional[ConditioningBundle] = None,
    ) -> RawTryOnOutput:
        """Executes virtual try-on inference using ConditioningBundle."""
        pass
