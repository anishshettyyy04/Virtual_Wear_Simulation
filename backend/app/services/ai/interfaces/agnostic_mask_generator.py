from abc import ABC, abstractmethod

from app.schemas.ai import (
    AgnosticMaskResult,
    GarmentInput,
    HumanParsingResult,
    PoseEstimationResult,
    PreprocessingResult,
)


class BaseAgnosticMaskGenerator(ABC):
    """Abstract interface defining clothing-agnostic mask generation stage."""

    @abstractmethod
    async def generate(
        self,
        preprocessed: PreprocessingResult,
        parsing: HumanParsingResult,
        pose: PoseEstimationResult,
        garment: GarmentInput,
    ) -> AgnosticMaskResult:
        """Asynchronously generates binary clothing-agnostic mask for VTON."""
        pass
