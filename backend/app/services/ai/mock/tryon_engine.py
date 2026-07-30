from app.schemas.ai import (
    HumanParsingResult,
    PoseEstimationResult,
    PreprocessingResult,
    RawTryOnOutput,
)
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.utils.logger import logger


class MockTryOnEngine(BaseTryOnEngine):
    """Deterministic mock virtual try-on engine implementation."""

    async def generate(
        self,
        preprocessed: PreprocessingResult,
        parsing: HumanParsingResult,
        pose: PoseEstimationResult,
    ) -> RawTryOnOutput:
        p_id = preprocessed.person_processed_id
        g_id = preprocessed.garment_processed_id
        logger.info(
            f"MockTryOnEngine: Generating VTON render for person '{p_id}' "
            f"and garment '{g_id}' using mask '{parsing.mask_id}' "
            f"and pose '{pose.pose_id}'"
        )
        return RawTryOnOutput(
            raw_render_id=f"raw_{p_id}_{g_id}",
            output_ref=f"mock://renders/raw_{p_id}_{g_id}.png",
            confidence_score=0.95,
            model_name="mock",
            model_version="1.0.0",
            metadata={
                "steps": 30,
                "sampler": "euler_a",
                "garment_warped": True,
            },
        )
