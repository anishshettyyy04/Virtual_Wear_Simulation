from fastapi import Depends

from app.api.dependencies.engines import get_tryon_engine
from app.services.ai.conditioning import ConditioningBuilder
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.services.ai.mock.agnostic_mask_generator import MockAgnosticMaskGenerator
from app.services.ai.mock.human_parser import MockHumanParser
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.preprocessor import MockPreprocessor
from app.services.ai.pipeline import VirtualWearPipeline


def get_virtual_wear_pipeline(
    engine: BaseTryOnEngine = Depends(get_tryon_engine),
) -> VirtualWearPipeline:
    """Dependency provider injecting fully configured VirtualWearPipeline."""
    return VirtualWearPipeline(
        preprocessor=MockPreprocessor(),
        human_parser=MockHumanParser(),
        pose_estimator=MockPoseEstimator(),
        agnostic_mask_generator=MockAgnosticMaskGenerator(),
        tryon_engine=engine,
        postprocessor=MockPostprocessor(),
        conditioning_adapter=ConditioningBuilder(),
    )
