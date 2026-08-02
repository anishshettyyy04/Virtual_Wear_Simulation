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
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.utils.logger import logger


class MockTryOnEngine(BaseTryOnEngine):
    """Deterministic mock virtual try-on engine implementation."""

    async def generate(
        self,
        preprocessed: Optional[PreprocessingResult] = None,
        parsing: Optional[HumanParsingResult] = None,
        pose: Optional[PoseEstimationResult] = None,
        agnostic_mask: Optional[AgnosticMaskResult] = None,
        garment: Optional[GarmentInput] = None,
        conditioning: Optional[ConditioningBundle] = None,
    ) -> RawTryOnOutput:
        if conditioning is not None:
            p_ref = conditioning.person_image_ref
            g_ref = conditioning.garment_image_ref
            mask_id = conditioning.agnostic_mask.mask_id
            logger.info(
                f"MockTryOnEngine: Generating VTON render using ConditioningBundle "
                f"'{conditioning.bundle_id}' for person '{p_ref}' and garment '{g_ref}'"
            )
            return RawTryOnOutput(
                raw_render_id=f"raw_{conditioning.bundle_id}",
                output_ref=f"mock://renders/raw_{conditioning.bundle_id}.png",
                confidence_score=0.95,
                model_name="mock",
                model_version="1.0.0",
                metadata={
                    "steps": 30,
                    "sampler": "euler_a",
                    "garment_warped": True,
                    "agnostic_mask_id": mask_id,
                },
            )

        if preprocessed is None or agnostic_mask is None:
            raise ValueError("Either conditioning bundle or canonical inputs required.")

        p_id = preprocessed.person_processed_id
        g_id = preprocessed.garment_processed_id
        parsing_id = parsing.mask_id if parsing else "none"
        pose_id = pose.pose_id if pose else "none"

        logger.info(
            f"MockTryOnEngine: Generating VTON render for person '{p_id}' "
            f"and garment '{g_id}' using parsing '{parsing_id}', "
            f"pose '{pose_id}', and agnostic mask '{agnostic_mask.mask_id}'"
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
                "agnostic_mask_id": agnostic_mask.mask_id,
            },
        )
