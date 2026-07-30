from app.schemas.ai import (
    GarmentInput,
    ImageDimensions,
    PersonInput,
    PreprocessingResult,
)
from app.services.ai.interfaces.preprocessor import BasePreprocessor
from app.utils.logger import logger


class MockPreprocessor(BasePreprocessor):
    """Deterministic mock preprocessor implementation."""

    async def process(
        self, person: PersonInput, garment: GarmentInput
    ) -> PreprocessingResult:
        logger.info(
            f"MockPreprocessor: Processing person '{person.person_id}' "
            f"and garment '{garment.garment_id}'"
        )
        p_dims = person.dimensions or ImageDimensions(width=1024, height=1024)
        g_dims = garment.dimensions or ImageDimensions(width=1024, height=1024)
        return PreprocessingResult(
            person_processed_id=f"proc_{person.person_id}",
            person_image_ref=f"mock://preprocessed/{person.person_id}.png",
            garment_processed_id=f"proc_{garment.garment_id}",
            garment_image_ref=f"mock://preprocessed/{garment.garment_id}.png",
            person_dimensions=p_dims,
            garment_dimensions=g_dims,
            normalized_metadata={
                "aspect_ratio_matched": True,
                "color_space": "sRGB",
            },
        )
