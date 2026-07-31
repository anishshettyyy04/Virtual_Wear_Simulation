import os

import numpy as np
import pytest
from PIL import Image

from app.config.settings import Settings
from app.schemas.ai import GarmentInput, PersonInput, TryOnResult
from app.services.ai.mock.human_parser import MockHumanParser
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.services.ai.parsing.labels import ProjectSemanticLabel
from app.services.ai.parsing.segformer_parser import SegFormerHumanParser
from app.services.ai.pipeline import VirtualWearPipeline
from app.services.ai.preprocessing.image_preprocessor import ImagePreprocessor
from tests.ai.test_segformer_parser import FakeImageProcessor, FakeSegFormerModel


@pytest.fixture
def sample_input_images(tmp_path):
    """Creates temporary person and garment input image files for integration."""
    person_dir = tmp_path / "raw_person"
    garment_dir = tmp_path / "raw_garment"
    person_dir.mkdir()
    garment_dir.mkdir()

    person_file = person_dir / "user_person.jpg"
    garment_file = garment_dir / "user_garment.jpg"

    Image.new("RGB", (400, 600), color=(200, 220, 240)).save(person_file)
    Image.new("RGB", (300, 300), color=(250, 200, 200)).save(garment_file)

    person = PersonInput(person_id="user_123", image_ref=str(person_file))
    garment = GarmentInput(garment_id="shirt_456", image_ref=str(garment_file))
    return person, garment, tmp_path


@pytest.mark.asyncio
async def test_pipeline_with_segformer_parser(sample_input_images):
    """Integration test: Real ImagePreprocessor + Real SegFormerParser (fake)."""
    person, garment, tmp_path = sample_input_images

    custom_settings = Settings(
        AI_PROCESSED_DIR=str(tmp_path / "processed"),
        AI_PREPROCESS_MAX_WIDTH=512,
        AI_PREPROCESS_MAX_HEIGHT=512,
    )
    preprocessor = ImagePreprocessor(config=custom_settings)
    segformer_parser = SegFormerHumanParser(
        model_name_or_path="mock/model",
        device="cpu",
        output_dir=str(tmp_path / "parsing"),
        image_processor=FakeImageProcessor(),
        model=FakeSegFormerModel(target_class_id=4),
    )
    pipeline = VirtualWearPipeline(
        preprocessor=preprocessor,
        human_parser=segformer_parser,
        pose_estimator=MockPoseEstimator(),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    result: TryOnResult = await pipeline.run(person, garment)

    assert result.final.final_image_id.startswith("final_")
    assert "segment_categories" in result.pipeline_metadata
    assert "UPPER_GARMENT" in result.pipeline_metadata["segment_categories"]
    assert "FACE" in result.pipeline_metadata["segment_categories"]

    # Verify semantic mask artifact exists on disk
    parsing_dir = tmp_path / "parsing"
    mask_files = list(parsing_dir.glob("*.png"))
    assert len(mask_files) == 1
    assert mask_files[0].exists()


@pytest.mark.asyncio
async def test_mock_human_parser_backward_compatibility(sample_input_images):
    """Verifies existing MockHumanParser remains fully functional."""
    person, garment, tmp_path = sample_input_images

    custom_settings = Settings(AI_PROCESSED_DIR=str(tmp_path / "processed"))
    pipeline = VirtualWearPipeline(
        preprocessor=ImagePreprocessor(config=custom_settings),
        human_parser=MockHumanParser(),
        pose_estimator=MockPoseEstimator(),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    result: TryOnResult = await pipeline.run(person, garment)
    assert result.final.final_image_id.startswith("final_")
    assert "head" in result.pipeline_metadata["segment_categories"]


@pytest.mark.smoke
@pytest.mark.skipif(
    os.environ.get("RUN_REAL_MODEL_TESTS") != "1",
    reason="Real SegFormer model smoke test skipped unless RUN_REAL_MODEL_TESTS=1",
)
@pytest.mark.asyncio
async def test_real_segformer_model_smoke_test(sample_input_images):
    """Optional smoke test running real Hugging Face SegFormer model."""
    person, garment, tmp_path = sample_input_images

    custom_settings = Settings(AI_PROCESSED_DIR=str(tmp_path / "processed"))
    preprocessor = ImagePreprocessor(config=custom_settings)
    human_parser = SegFormerHumanParser(
        model_name_or_path="mattmdjaga/segformer_b2_clothes",
        device="cpu",
        output_dir=str(tmp_path / "real_parsing"),
    )
    pipeline = VirtualWearPipeline(
        preprocessor=preprocessor,
        human_parser=human_parser,
        pose_estimator=MockPoseEstimator(),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    result = await pipeline.run(person, garment)
    assert result.final.final_image_id.startswith("final_")
    assert len(result.pipeline_metadata["segment_categories"]) > 0

    # Verify generated real parsing artifact
    parsing_dir = tmp_path / "real_parsing"
    mask_files = list(parsing_dir.glob("*.png"))
    assert len(mask_files) == 1
    mask_file = mask_files[0]
    assert mask_file.exists()

    with Image.open(mask_file) as mask_img:
        assert mask_img.format == "PNG"
        assert mask_img.mode == "L"
        # Mask dimensions match processed person dimensions (400, 600)
        assert mask_img.size == (400, 600)

        mask_arr = np.array(mask_img)
        unique_pixels = set(np.unique(mask_arr))
        valid_values = {int(label) for label in ProjectSemanticLabel}
        assert unique_pixels.issubset(valid_values)
