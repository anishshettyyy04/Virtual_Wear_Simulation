from abc import ABC, abstractmethod

from app.schemas.ai import PostprocessingResult, RawTryOnOutput


class BasePostprocessor(ABC):
    """Abstract interface defining final image postprocessing & enhancement stage."""

    @abstractmethod
    async def process(self, raw_output: RawTryOnOutput) -> PostprocessingResult:
        """Applies format encoding, resolution scaling, and artifact cleanup."""
        pass
