from abc import ABC, abstractmethod

from app.schemas.ai import HumanParsingResult, PreprocessingResult


class BaseHumanParser(ABC):
    """Abstract interface defining human body parsing / segmentation stage."""

    @abstractmethod
    async def parse(self, preprocessed: PreprocessingResult) -> HumanParsingResult:
        """Extracts human parsing / clothing segmentation regions."""
        pass
