from abc import ABC, abstractmethod

from app.schemas.ai import GarmentInput, PersonInput, PreprocessingResult


class BasePreprocessor(ABC):
    """Abstract interface defining person and garment preprocessing stage."""

    @abstractmethod
    async def process(
        self, person: PersonInput, garment: GarmentInput
    ) -> PreprocessingResult:
        """Validates and normalizes person avatar and garment inputs."""
        pass
