import asyncio
from typing import List

import pytest

from app.schemas.ai import GarmentInput, ImageDimensions, PersonInput, TryOnResult
from app.services.ai.exceptions import (
    HumanParsingError,
    PoseEstimationError,
    PostprocessingError,
    PreprocessingError,
    TryOnInferenceError,
)
from app.services.ai.interfaces.human_parser import BaseHumanParser
from app.services.ai.interfaces.pose_estimator import BasePoseEstimator
from app.services.ai.interfaces.postprocessor import BasePostprocessor
from app.services.ai.interfaces.preprocessor import BasePreprocessor
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.services.ai.mock.human_parser import MockHumanParser
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.preprocessor import MockPreprocessor
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.services.ai.pipeline import VirtualWearPipeline


@pytest.mark.asyncio
async def test_full_mock_pipeline_execution() -> None:
    """Verifies end-to-end execution of VirtualWearPipeline using mock stages."""
    pipeline = VirtualWearPipeline(
        preprocessor=MockPreprocessor(),
        human_parser=MockHumanParser(),
        pose_estimator=MockPoseEstimator(),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    person = PersonInput(
        person_id="person_100",
        image_ref="mock://avatars/p100.jpg",
        dimensions=ImageDimensions(width=1024, height=1024),
    )
    garment = GarmentInput(
        garment_id="shirt_200",
        image_ref="mock://garments/g200.jpg",
        category="upper_body",
        dimensions=ImageDimensions(width=1024, height=1024),
    )

    result = await pipeline.run(person, garment)

    assert isinstance(result, TryOnResult)
    assert result.final.final_image_id == "final_raw_proc_person_100_proc_shirt_200"
    assert result.final.output_ref.startswith("mock://results/")
    assert result.pipeline_metadata["model_name"] == "mock"
    assert result.pipeline_metadata["confidence_score"] == 0.95


@pytest.mark.asyncio
async def test_pipeline_stage_ordering_spy() -> None:
    """Verifies that pipeline stages execute in strict order via spy tracking."""
    execution_order: List[str] = []

    class SpyPreprocessor(BasePreprocessor):
        async def process(self, person, garment):
            execution_order.append("preprocessor")
            return await MockPreprocessor().process(person, garment)

    class SpyHumanParser(BaseHumanParser):
        async def parse(self, preprocessed):
            execution_order.append("human_parser")
            return await MockHumanParser().parse(preprocessed)

    class SpyPoseEstimator(BasePoseEstimator):
        async def estimate(self, preprocessed):
            execution_order.append("pose_estimator")
            return await MockPoseEstimator().estimate(preprocessed)

    class SpyTryOnEngine(BaseTryOnEngine):
        async def generate(self, preprocessed, parsing, pose):
            execution_order.append("tryon_engine")
            return await MockTryOnEngine().generate(preprocessed, parsing, pose)

    class SpyPostprocessor(BasePostprocessor):
        async def process(self, raw_output):
            execution_order.append("postprocessor")
            return await MockPostprocessor().process(raw_output)

    pipeline = VirtualWearPipeline(
        preprocessor=SpyPreprocessor(),
        human_parser=SpyHumanParser(),
        pose_estimator=SpyPoseEstimator(),
        tryon_engine=SpyTryOnEngine(),
        postprocessor=SpyPostprocessor(),
    )

    person = PersonInput(person_id="p", image_ref="ref")
    garment = GarmentInput(garment_id="g", image_ref="ref")

    await pipeline.run(person, garment)

    assert execution_order[0] == "preprocessor"
    assert set(execution_order[1:3]) == {"human_parser", "pose_estimator"}
    assert execution_order[3] == "tryon_engine"
    assert execution_order[4] == "postprocessor"


@pytest.mark.asyncio
async def test_concurrent_parsing_and_pose_execution() -> None:
    """Verifies parsing and pose execute concurrently via asyncio.Event."""
    event_parser_started = asyncio.Event()
    event_pose_started = asyncio.Event()

    class ConcurrentHumanParser(BaseHumanParser):
        async def parse(self, preprocessed):
            event_parser_started.set()
            await event_pose_started.wait()
            return await MockHumanParser().parse(preprocessed)

    class ConcurrentPoseEstimator(BasePoseEstimator):
        async def estimate(self, preprocessed):
            event_pose_started.set()
            await event_parser_started.wait()
            return await MockPoseEstimator().estimate(preprocessed)

    pipeline = VirtualWearPipeline(
        preprocessor=MockPreprocessor(),
        human_parser=ConcurrentHumanParser(),
        pose_estimator=ConcurrentPoseEstimator(),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    person = PersonInput(person_id="p", image_ref="ref")
    garment = GarmentInput(garment_id="g", image_ref="ref")

    result = await asyncio.wait_for(pipeline.run(person, garment), timeout=2.0)
    assert result is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failing_stage,expected_exception",
    [
        ("preprocessor", PreprocessingError),
        ("human_parser", HumanParsingError),
        ("pose_estimator", PoseEstimationError),
        ("tryon_engine", TryOnInferenceError),
        ("postprocessor", PostprocessingError),
    ],
)
async def test_pipeline_stage_failure_propagation(
    failing_stage: str, expected_exception: type
) -> None:
    """Verifies stage failure stops execution and raises appropriate exception."""

    class FailingPreprocessor(MockPreprocessor):
        async def process(self, person, garment):
            if failing_stage == "preprocessor":
                raise RuntimeError("Custom preprocessor internal error")
            return await super().process(person, garment)

    class FailingHumanParser(MockHumanParser):
        async def parse(self, preprocessed):
            if failing_stage == "human_parser":
                raise HumanParsingError("Custom parsing exception")
            return await super().parse(preprocessed)

    class FailingPoseEstimator(MockPoseEstimator):
        async def estimate(self, preprocessed):
            if failing_stage == "pose_estimator":
                raise PoseEstimationError("Custom pose exception")
            return await super().estimate(preprocessed)

    class FailingTryOnEngine(MockTryOnEngine):
        async def generate(self, preprocessed, parsing, pose):
            if failing_stage == "tryon_engine":
                raise RuntimeError("Custom VTON engine failure")
            return await super().generate(preprocessed, parsing, pose)

    class FailingPostprocessor(MockPostprocessor):
        async def process(self, raw_output):
            if failing_stage == "postprocessor":
                raise PostprocessingError("Custom postprocessing exception")
            return await super().process(raw_output)

    pipeline = VirtualWearPipeline(
        preprocessor=FailingPreprocessor(),
        human_parser=FailingHumanParser(),
        pose_estimator=FailingPoseEstimator(),
        tryon_engine=FailingTryOnEngine(),
        postprocessor=FailingPostprocessor(),
    )

    person = PersonInput(person_id="p", image_ref="ref")
    garment = GarmentInput(garment_id="g", image_ref="ref")

    with pytest.raises(expected_exception):
        await pipeline.run(person, garment)
