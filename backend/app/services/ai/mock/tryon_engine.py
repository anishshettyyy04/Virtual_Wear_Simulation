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
from app.services.ai.engines.common.metrics import InferenceMetrics
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.utils.logger import logger


class MockTryOnEngine(BaseTryOnEngine):
    """Deterministic mock virtual try-on engine implementation."""

    async def warmup(self) -> None:
        """Mock warm-up execution."""
        logger.info("MockTryOnEngine: Warm-up completed.")

    async def generate(
        self,
        preprocessed: Optional[PreprocessingResult] = None,
        parsing: Optional[HumanParsingResult] = None,
        pose: Optional[PoseEstimationResult] = None,
        agnostic_mask: Optional[AgnosticMaskResult] = None,
        garment: Optional[GarmentInput] = None,
        conditioning: Optional[ConditioningBundle] = None,
    ) -> RawTryOnOutput:
        metrics = InferenceMetrics(
            inference_time_ms=150.0,
            preprocessing_time_ms=10.0,
            loading_time_ms=5.0,
            total_time_ms=165.0,
            device="cpu",
            dtype="fp32",
            scheduler="euler_a",
            inference_steps=30,
            guidance_scale=2.0,
        )

        canonical_meta = {
            "engine": "mock_vton",
            "engine_version": "1.0.0",
            "pipeline_version": "1.0.0",
            "model_revision": "mock",
            "device": "cpu",
            "dtype": "fp32",
            "offload_mode": "none",
            "scheduler": "euler_a",
            "generator": "MockTryOnEngine",
            "metrics": metrics.model_dump(),
        }

        if preprocessed is not None:
            p_id = preprocessed.person_processed_id
            g_id = preprocessed.garment_processed_id
            parsing_id = parsing.mask_id if parsing else "none"
            pose_id = pose.pose_id if pose else "none"
            mask_id = agnostic_mask.mask_id if agnostic_mask else "none"

            logger.info(
                f"MockTryOnEngine: Generating VTON render for person '{p_id}' "
                f"and garment '{g_id}' using parsing '{parsing_id}', "
                f"pose '{pose_id}', and agnostic mask '{mask_id}'"
            )
            canonical_meta["agnostic_mask_id"] = mask_id
            return RawTryOnOutput(
                raw_render_id=f"raw_{p_id}_{g_id}",
                output_ref=f"mock://renders/raw_{p_id}_{g_id}.png",
                confidence_score=0.95,
                model_name="mock",
                model_version="1.0.0",
                metadata=canonical_meta,
            )

        if conditioning is not None:
            p_ref = conditioning.person_image_ref
            g_ref = conditioning.garment_image_ref
            mask_id = conditioning.agnostic_mask.mask_id
            logger.info(
                f"MockTryOnEngine: Generating VTON render using ConditioningBundle "
                f"'{conditioning.bundle_id}' for person '{p_ref}' and garment '{g_ref}'"
            )
            canonical_meta["agnostic_mask_id"] = mask_id
            return RawTryOnOutput(
                raw_render_id=f"raw_{conditioning.bundle_id}",
                output_ref=f"mock://renders/raw_{conditioning.bundle_id}.png",
                confidence_score=0.95,
                model_name="mock",
                model_version="1.0.0",
                metadata=canonical_meta,
            )

        raise ValueError("Either preprocessed or conditioning inputs required.")
