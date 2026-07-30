from abc import ABC, abstractmethod

from app.schemas.ai import (
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
        preprocessed: PreprocessingResult,
        parsing: HumanParsingResult,
        pose: PoseEstimationResult,
    ) -> RawTryOnOutput:
        """Executes virtual try-on inference combining person, garment, and pose."""
        pass
