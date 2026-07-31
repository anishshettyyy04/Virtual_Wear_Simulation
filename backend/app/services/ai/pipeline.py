import asyncio
from typing import Any, Dict

from app.schemas.ai import GarmentInput, PersonInput, TryOnResult
from app.services.ai.exceptions import (
    AgnosticMaskError,
    AIPipelineError,
    HumanParsingError,
    PostprocessingError,
    PreprocessingError,
    TryOnInferenceError,
)
from app.services.ai.interfaces.agnostic_mask_generator import (
    BaseAgnosticMaskGenerator,
)
from app.services.ai.interfaces.human_parser import BaseHumanParser
from app.services.ai.interfaces.pose_estimator import BasePoseEstimator
from app.services.ai.interfaces.postprocessor import BasePostprocessor
from app.services.ai.interfaces.preprocessor import BasePreprocessor
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.utils.logger import logger


class VirtualWearPipeline:
    """Orchestrates model-agnostic virtual try-on AI pipeline stages."""

    def __init__(
        self,
        preprocessor: BasePreprocessor,
        human_parser: BaseHumanParser,
        pose_estimator: BasePoseEstimator,
        agnostic_mask_generator: BaseAgnosticMaskGenerator,
        tryon_engine: BaseTryOnEngine,
        postprocessor: BasePostprocessor,
    ) -> None:
        self.preprocessor = preprocessor
        self.human_parser = human_parser
        self.pose_estimator = pose_estimator
        self.agnostic_mask_generator = agnostic_mask_generator
        self.tryon_engine = tryon_engine
        self.postprocessor = postprocessor

    async def run(self, person: PersonInput, garment: GarmentInput) -> TryOnResult:
        """Executes full try-on pipeline sequentially & concurrently."""
        logger.info(
            f"AI Pipeline: Starting virtual wear simulation for person "
            f"'{person.person_id}' and garment '{garment.garment_id}'"
        )

        # Stage 1: Preprocessing
        logger.info("AI Pipeline: Stage 1 - Preprocessing started")
        try:
            preprocessed = await self.preprocessor.process(person, garment)
        except AIPipelineError:
            raise
        except Exception as exc:
            raise PreprocessingError(
                f"Preprocessing stage failed: {exc}", details=str(exc)
            ) from exc
        logger.info("AI Pipeline: Stage 1 - Preprocessing completed")

        # Stage 2: Concurrent Human Parsing & Pose Estimation
        logger.info(
            "AI Pipeline: Stage 2 - Concurrent Human Parsing & "
            "Pose Estimation started"
        )
        try:
            parsing_result, pose_result = await asyncio.gather(
                self.human_parser.parse(preprocessed),
                self.pose_estimator.estimate(preprocessed),
            )
        except AIPipelineError:
            raise
        except Exception as exc:
            raise HumanParsingError(
                f"Concurrent stage execution failed: {exc}", details=str(exc)
            ) from exc

        logger.info(
            "AI Pipeline: Stage 2 - Concurrent Human Parsing & "
            "Pose Estimation completed"
        )

        # Stage 3: Agnostic Mask Generation
        logger.info("AI Pipeline: Stage 3 - Agnostic Mask Generation started")
        try:
            agnostic_mask = await self.agnostic_mask_generator.generate(
                preprocessed, parsing_result, pose_result, garment
            )
        except AIPipelineError:
            raise
        except Exception as exc:
            raise AgnosticMaskError(
                f"Agnostic Mask Generation stage failed: {exc}", details=str(exc)
            ) from exc
        logger.info("AI Pipeline: Stage 3 - Agnostic Mask Generation completed")

        # Stage 4: Virtual Try-On Neural Inference Engine
        logger.info("AI Pipeline: Stage 4 - Virtual Try-On Engine inference started")
        try:
            raw_output = await self.tryon_engine.generate(
                preprocessed, parsing_result, pose_result, agnostic_mask, garment
            )
        except AIPipelineError:
            raise
        except Exception as exc:
            raise TryOnInferenceError(
                f"Try-On Engine inference stage failed: {exc}", details=str(exc)
            ) from exc
        logger.info("AI Pipeline: Stage 4 - Virtual Try-On Engine inference completed")

        # Stage 5: Postprocessing & Final Render Encoding
        logger.info("AI Pipeline: Stage 5 - Postprocessing started")
        try:
            final_result = await self.postprocessor.process(raw_output)
        except AIPipelineError:
            raise
        except Exception as exc:
            raise PostprocessingError(
                f"Postprocessing stage failed: {exc}", details=str(exc)
            ) from exc
        logger.info("AI Pipeline: Stage 5 - Postprocessing completed")

        pipeline_metadata: Dict[str, Any] = {
            "model_name": raw_output.model_name,
            "model_version": raw_output.model_version,
            "confidence_score": raw_output.confidence_score,
            "num_keypoints": pose_result.num_keypoints,
            "segment_categories": parsing_result.segment_categories,
            "agnostic_mask_id": agnostic_mask.mask_id,
            "replace_coverage": agnostic_mask.replace_coverage,
        }

        logger.info("AI Pipeline: Execution completed successfully")
        return TryOnResult(final=final_result, pipeline_metadata=pipeline_metadata)
