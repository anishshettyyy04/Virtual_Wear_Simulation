from app.schemas.ai import (
    AgnosticMaskResult,
    GarmentInput,
    HumanParsingResult,
    PoseEstimationResult,
    PreprocessingResult,
)
from app.services.ai.interfaces.agnostic_mask_generator import (
    BaseAgnosticMaskGenerator,
)
from app.utils.logger import logger


class MockAgnosticMaskGenerator(BaseAgnosticMaskGenerator):
    """Deterministic mock clothing-agnostic mask generator implementation."""

    async def generate(
        self,
        preprocessed: PreprocessingResult,
        parsing: HumanParsingResult,
        pose: PoseEstimationResult,
        garment: GarmentInput,
    ) -> AgnosticMaskResult:
        p_id = preprocessed.person_processed_id
        category_str = (
            garment.category.value
            if hasattr(garment.category, "value")
            else str(garment.category)
        )

        logger.info(
            f"MockAgnosticMaskGenerator: Generating mock mask for person '{p_id}' "
            f"category '{category_str}'"
        )

        return AgnosticMaskResult(
            mask_id=f"mock_agnostic_mask_{p_id}",
            mask_ref=f"mock://masks/agnostic_{p_id}.png",
            garment_category=category_str,
            dimensions=preprocessed.person_dimensions,
            replace_coverage=0.25,
            metadata={
                "mock": True,
                "schema_version": "v1",
            },
        )
