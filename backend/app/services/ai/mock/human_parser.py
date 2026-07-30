from app.schemas.ai import HumanParsingResult, PreprocessingResult
from app.services.ai.interfaces.human_parser import BaseHumanParser
from app.utils.logger import logger


class MockHumanParser(BaseHumanParser):
    """Deterministic mock human parser implementation."""

    async def parse(self, preprocessed: PreprocessingResult) -> HumanParsingResult:
        logger.info(
            f"MockHumanParser: Parsing body regions for person "
            f"'{preprocessed.person_processed_id}'"
        )
        return HumanParsingResult(
            mask_id=f"mask_{preprocessed.person_processed_id}",
            mask_ref=f"mock://masks/mask_{preprocessed.person_processed_id}.png",
            segment_categories=[
                "head",
                "hair",
                "upper_body",
                "lower_body",
                "background",
            ],
            metadata={"parser_name": "mock_parser", "confidence": 0.99},
        )
