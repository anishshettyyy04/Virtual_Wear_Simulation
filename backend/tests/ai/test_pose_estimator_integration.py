import os
from pathlib import Path

import pytest
from PIL import Image

from app.config.settings import Settings
from app.schemas.ai import GarmentInput, PersonInput, TryOnResult
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.services.ai.parsing import SegFormerHumanParser
from app.services.ai.pipeline import VirtualWearPipeline
from app.services.ai.pose import DWPoseEstimator
from app.services.ai.preprocessing import ImagePreprocessor
from tests.ai.test_dwpose_estimator import (
    FakeONNXDetectorSession,
    FakeONNXPoseSession,
)
from tests.ai.test_segformer_parser import FakeImageProcessor, FakeSegFormerModel


@pytest.fixture
def sample_input_images(tmp_path: Path):
    person_path = tmp_path / "raw_person.jpg"
    garment_path = tmp_path / "raw_garment.jpg"

    p_img = Image.new("RGB", (768, 1024), color=(220, 200, 180))
    g_img = Image.new("RGB", (768, 1024), color=(50, 100, 200))

    p_img.save(person_path, format="JPEG")
    g_img.save(garment_path, format="JPEG")

    return person_path, garment_path


@pytest.mark.asyncio
async def test_pipeline_integration_with_dwpose_estimator(
    sample_input_images, tmp_path: Path
):
    """Test VirtualWearPipeline end-to-end with DWPoseEstimator."""

    person_path, garment_path = sample_input_images

    # Configure temporary directories via Settings
    test_settings = Settings(
        AI_PROCESSED_DIR=str(tmp_path / "processed"),
        AI_HUMAN_PARSER_OUTPUT_DIR=str(tmp_path / "processed" / "parsing"),
        AI_POSE_OUTPUT_DIR=str(tmp_path / "processed" / "poses"),
    )

    preprocessor = ImagePreprocessor(config=test_settings)
    human_parser = SegFormerHumanParser(
        device="cpu",
        output_dir=str(tmp_path / "processed" / "parsing"),
        image_processor=FakeImageProcessor(),
        model=FakeSegFormerModel(),
    )
    pose_estimator = DWPoseEstimator(
        device="cpu",
        output_dir=str(tmp_path / "processed" / "poses"),
        detector_session=FakeONNXDetectorSession(),
        pose_session=FakeONNXPoseSession(),
    )
    tryon_engine = MockTryOnEngine()
    postprocessor = MockPostprocessor()

    pipeline = VirtualWearPipeline(
        preprocessor=preprocessor,
        human_parser=human_parser,
        pose_estimator=pose_estimator,
        tryon_engine=tryon_engine,
        postprocessor=postprocessor,
    )

    person = PersonInput(person_id="p_int_001", image_ref=str(person_path))
    garment = GarmentInput(garment_id="g_int_001", image_ref=str(garment_path))

    result = await pipeline.run(person, garment)

    assert isinstance(result, TryOnResult)
    assert result.final.output_ref.startswith("mock://results/")
    assert result.final.final_image_id.startswith(
        "final_raw_proc_p_int_001_proc_g_int_001"
    )


@pytest.mark.asyncio
async def test_mock_pose_estimator_backward_compatibility(
    sample_input_images, tmp_path: Path
):
    """Verify pipeline functions seamlessly with MockPoseEstimator."""
    person_path, garment_path = sample_input_images

    pipeline = VirtualWearPipeline(
        preprocessor=ImagePreprocessor(
            config=Settings(AI_PROCESSED_DIR=str(tmp_path / "proc"))
        ),
        human_parser=SegFormerHumanParser(
            device="cpu",
            output_dir=str(tmp_path / "parse"),
            image_processor=FakeImageProcessor(),
            model=FakeSegFormerModel(),
        ),
        pose_estimator=MockPoseEstimator(),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    result = await pipeline.run(
        PersonInput(person_id="p_mock_001", image_ref=str(person_path)),
        GarmentInput(garment_id="g_mock_001", image_ref=str(garment_path)),
    )

    assert isinstance(result, TryOnResult)
    assert result.final.final_image_id == "final_raw_proc_p_mock_001_proc_g_mock_001"


@pytest.mark.pose_smoke
@pytest.mark.skipif(
    os.getenv("RUN_REAL_POSE_TESTS") != "1",
    reason="Real ONNX DWPose smoke test skipped unless RUN_REAL_POSE_TESTS=1",
)
@pytest.mark.asyncio
async def test_real_dwpose_model_smoke_test(sample_input_images, tmp_path: Path):
    """Optional end-to-end smoke test using real YOLOX detector & DWPose ONNX models."""
    person_path, garment_path = sample_input_images

    test_settings = Settings(
        AI_PROCESSED_DIR=str(tmp_path / "processed"),
        AI_HUMAN_PARSER_OUTPUT_DIR=str(tmp_path / "processed" / "parsing"),
        AI_POSE_OUTPUT_DIR=str(tmp_path / "processed" / "poses"),
    )

    pipeline = VirtualWearPipeline(
        preprocessor=ImagePreprocessor(config=test_settings),
        human_parser=SegFormerHumanParser(
            device="cpu",
            output_dir=str(tmp_path / "processed" / "parsing"),
            image_processor=FakeImageProcessor(),
            model=FakeSegFormerModel(),
        ),
        pose_estimator=DWPoseEstimator(
            device="cpu",
            output_dir=str(tmp_path / "processed" / "poses"),
        ),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    result = await pipeline.run(
        PersonInput(person_id="real_pose_person", image_ref=str(person_path)),
        GarmentInput(garment_id="real_pose_garment", image_ref=str(garment_path)),
    )

    assert isinstance(result, TryOnResult)
    assert result.final.final_image_id.startswith(
        "final_raw_proc_real_pose_person_proc_real_pose_garment"
    )
