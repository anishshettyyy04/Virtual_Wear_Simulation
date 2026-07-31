import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app.schemas.ai import (
    GarmentCategory,
    GarmentInput,
    HumanParsingResult,
    ImageDimensions,
    PersonInput,
    PoseEstimationResult,
    PreprocessingResult,
)
from app.services.ai.exceptions import AgnosticMaskError
from app.services.ai.masking.generator import AgnosticMaskGenerator
from app.services.ai.mock.human_parser import MockHumanParser
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.preprocessor import MockPreprocessor
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.services.ai.parsing.labels import ProjectSemanticLabel
from app.services.ai.pipeline import VirtualWearPipeline


@pytest.fixture
def mask_test_fixtures(tmp_path: Path):
    """Creates synthetic parsing mask and pose artifacts for generator tests."""

    img_w, img_h = 400, 600
    person_img_path = tmp_path / "processed_person.jpg"
    person_img = Image.new("RGB", (img_w, img_h), (200, 200, 200))
    person_img.save(person_img_path, format="JPEG")

    # Create synthetic parsing mask array
    parsing_arr = np.zeros((img_h, img_w), dtype=np.uint8)

    # Face (label 2): top center
    parsing_arr[50:120, 150:250] = int(ProjectSemanticLabel.FACE)
    # Hair (label 1): above face
    parsing_arr[20:50, 140:260] = int(ProjectSemanticLabel.HAIR)
    # Upper Garment (label 4): torso region
    parsing_arr[150:350, 120:280] = int(ProjectSemanticLabel.UPPER_GARMENT)
    # Lower Garment (label 5): legs region
    parsing_arr[350:520, 130:270] = int(ProjectSemanticLabel.LOWER_GARMENT)
    # Footwear (label 11): feet region
    parsing_arr[520:580, 140:260] = int(ProjectSemanticLabel.FOOTWEAR)

    mask_path = tmp_path / "synthetic_parsing.png"
    Image.fromarray(parsing_arr, mode="L").save(mask_path, format="PNG")

    # Create synthetic pose JSON artifact
    pose_json_data = {
        "schema_version": "v1",
        "topology": "COCO_18",
        "image": {"width": img_w, "height": img_h},
        "keypoints": [
            {
                "id": 0,
                "name": "NOSE",
                "x_px": 200,
                "y_px": 80,
                "confidence": 0.9,
                "visible": True,
            },
            {
                "id": 1,
                "name": "NECK",
                "x_px": 200,
                "y_px": 140,
                "confidence": 0.9,
                "visible": True,
            },
            {
                "id": 2,
                "name": "RIGHT_SHOULDER",
                "x_px": 130,
                "y_px": 160,
                "confidence": 0.9,
                "visible": True,
            },
            {
                "id": 3,
                "name": "RIGHT_ELBOW",
                "x_px": 100,
                "y_px": 250,
                "confidence": 0.9,
                "visible": True,
            },
            {
                "id": 4,
                "name": "RIGHT_WRIST",
                "x_px": 90,
                "y_px": 330,
                "confidence": 0.9,
                "visible": True,
            },
            {
                "id": 5,
                "name": "LEFT_SHOULDER",
                "x_px": 270,
                "y_px": 160,
                "confidence": 0.9,
                "visible": True,
            },
            {
                "id": 6,
                "name": "LEFT_ELBOW",
                "x_px": 300,
                "y_px": 250,
                "confidence": 0.9,
                "visible": True,
            },
            {
                "id": 7,
                "name": "LEFT_WRIST",
                "x_px": 310,
                "y_px": 330,
                "confidence": 0.9,
                "visible": True,
            },
            {
                "id": 8,
                "name": "RIGHT_HIP",
                "x_px": 150,
                "y_px": 350,
                "confidence": 0.9,
                "visible": True,
            },
            {
                "id": 11,
                "name": "LEFT_HIP",
                "x_px": 250,
                "y_px": 350,
                "confidence": 0.9,
                "visible": True,
            },
        ],
    }

    pose_path = tmp_path / "synthetic_pose.json"
    with open(pose_path, "w", encoding="utf-8") as f:
        json.dump(pose_json_data, f)

    preprocessed = PreprocessingResult(
        person_processed_id="proc_person_001",
        garment_processed_id="proc_shirt_001",
        person_image_ref=str(person_img_path),
        garment_image_ref=str(person_img_path),
        person_dimensions=ImageDimensions(width=img_w, height=img_h),
        garment_dimensions=ImageDimensions(width=img_w, height=img_h),
    )

    parsing_result = HumanParsingResult(
        mask_id="mask_001",
        mask_ref=str(mask_path),
        segment_categories=["upper_garment", "lower_garment", "face", "hair"],
        dimensions=ImageDimensions(width=img_w, height=img_h),
    )

    pose_result = PoseEstimationResult(
        pose_id="pose_001",
        pose_ref=str(pose_path),
        topology="COCO_18",
        num_keypoints=10,
        dimensions=ImageDimensions(width=img_w, height=img_h),
    )

    return preprocessed, parsing_result, pose_result, tmp_path


@pytest.mark.asyncio
async def test_real_agnostic_mask_generator_upper_body(mask_test_fixtures):
    """Verifies RealAgnosticMaskGenerator creates valid upper-body agnostic mask."""
    preprocessed, parsing_result, pose_result, tmp_path = mask_test_fixtures

    generator = AgnosticMaskGenerator(output_dir=str(tmp_path / "masks"))
    garment = GarmentInput(
        garment_id="g1", image_ref="ref", category=GarmentCategory.UPPER_BODY
    )

    result = await generator.generate(
        preprocessed, parsing_result, pose_result, garment
    )

    assert result.garment_category == "upper_body"
    assert result.replace_coverage > 0.0
    assert result.replace_coverage < 0.60
    assert Path(result.mask_ref).exists()

    with Image.open(result.mask_ref) as mask_img:
        assert mask_img.format == "PNG"
        assert mask_img.mode == "L"
        assert mask_img.size == (400, 600)

        mask_arr = np.array(mask_img)
        unique_vals = set(np.unique(mask_arr))
        assert unique_vals.issubset({0, 255})

        # Verify face region (y: 50..120, x: 150..250) is 0 (Preserved)
        face_region = mask_arr[50:120, 150:250]
        assert np.all(face_region == 0)


@pytest.mark.asyncio
async def test_real_agnostic_mask_generator_lower_body(mask_test_fixtures):
    """Verifies lower-body agnostic mask generation."""
    preprocessed, parsing_result, pose_result, tmp_path = mask_test_fixtures

    generator = AgnosticMaskGenerator(output_dir=str(tmp_path / "masks"))
    garment = GarmentInput(
        garment_id="g2", image_ref="ref", category=GarmentCategory.LOWER_BODY
    )

    result = await generator.generate(
        preprocessed, parsing_result, pose_result, garment
    )

    assert result.garment_category == "lower_body"
    assert result.replace_coverage > 0.0
    assert Path(result.mask_ref).exists()


@pytest.mark.asyncio
async def test_real_agnostic_mask_generator_full_body(mask_test_fixtures):
    """Verifies full-body agnostic mask generation."""
    preprocessed, parsing_result, pose_result, tmp_path = mask_test_fixtures

    generator = AgnosticMaskGenerator(output_dir=str(tmp_path / "masks"))
    garment = GarmentInput(
        garment_id="g3", image_ref="ref", category=GarmentCategory.FULL_BODY
    )

    result = await generator.generate(
        preprocessed, parsing_result, pose_result, garment
    )

    assert result.garment_category == "full_body"
    assert result.replace_coverage > 0.0
    assert Path(result.mask_ref).exists()


@pytest.mark.asyncio
async def test_agnostic_mask_generator_invalid_category(mask_test_fixtures):
    """Verifies invalid garment category raises AgnosticMaskError."""
    preprocessed, parsing_result, pose_result, tmp_path = mask_test_fixtures
    generator = AgnosticMaskGenerator(output_dir=str(tmp_path / "masks"))

    garment = GarmentInput(garment_id="g_bad", image_ref="ref", category="invalid_cat")
    with pytest.raises(AgnosticMaskError, match="Unsupported garment category"):
        await generator.generate(preprocessed, parsing_result, pose_result, garment)


@pytest.mark.asyncio
async def test_agnostic_mask_generator_missing_parsing_artifact(mask_test_fixtures):
    """Verifies missing parsing artifact raises AgnosticMaskError."""
    preprocessed, parsing_result, pose_result, tmp_path = mask_test_fixtures
    generator = AgnosticMaskGenerator(output_dir=str(tmp_path / "masks"))

    bad_parsing = HumanParsingResult(
        mask_id="m_bad",
        mask_ref=str(tmp_path / "non_existent.png"),
        segment_categories=[],
    )
    garment = GarmentInput(garment_id="g1", image_ref="ref", category="upper_body")

    with pytest.raises(AgnosticMaskError, match="does not exist"):
        await generator.generate(preprocessed, bad_parsing, pose_result, garment)


@pytest.mark.asyncio
async def test_pipeline_with_real_agnostic_mask_generator(mask_test_fixtures):
    """Verifies pipeline execution with Real AgnosticMaskGenerator."""

    preprocessed, parsing_result, pose_result, tmp_path = mask_test_fixtures

    class CustomPreprocessor(MockPreprocessor):
        async def process(self, person, garment):
            return preprocessed

    class CustomParser(MockHumanParser):
        async def parse(self, preprocessed):
            return parsing_result

    class CustomPose(MockPoseEstimator):
        async def estimate(self, preprocessed):
            return pose_result

    pipeline = VirtualWearPipeline(
        preprocessor=CustomPreprocessor(),
        human_parser=CustomParser(),
        pose_estimator=CustomPose(),
        agnostic_mask_generator=AgnosticMaskGenerator(
            output_dir=str(tmp_path / "masks")
        ),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    person = PersonInput(person_id="p1", image_ref="ref")
    garment = GarmentInput(garment_id="g1", image_ref="ref", category="upper_body")

    result = await pipeline.run(person, garment)
    assert result.final is not None
    assert "agnostic_mask_id" in result.pipeline_metadata
