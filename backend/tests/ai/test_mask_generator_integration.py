import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw

from app.config.settings import Settings
from app.schemas.ai import GarmentCategory, GarmentInput, PersonInput, TryOnResult
from app.services.ai.masking.generator import AgnosticMaskGenerator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.services.ai.parsing import SegFormerHumanParser
from app.services.ai.pipeline import VirtualWearPipeline
from app.services.ai.pose import DWPoseEstimator
from app.services.ai.preprocessing import ImagePreprocessor


@pytest.fixture
def sample_input_images(tmp_path: Path):
    """Creates temporary person and garment input image files for testing."""
    person_dir = tmp_path / "raw_person"
    garment_dir = tmp_path / "raw_garment"
    person_dir.mkdir()
    garment_dir.mkdir()

    person_path = person_dir / "person.jpg"
    garment_path = garment_dir / "garment.jpg"

    # Create synthetic person photo with drawn head & torso
    img = Image.new("RGB", (768, 1024), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([334, 100, 434, 200], fill=(210, 160, 130))  # Head
    draw.rectangle([300, 200, 468, 600], fill=(50, 80, 200))  # Torso/Shirt
    draw.rectangle([310, 600, 370, 950], fill=(40, 40, 100))  # Left Leg
    draw.rectangle([390, 600, 450, 950], fill=(40, 40, 100))  # Right Leg
    img.save(person_path, format="JPEG")

    garment_img = Image.new("RGB", (800, 800), (220, 50, 50))
    garment_img.save(garment_path, format="JPEG")

    return person_path, garment_path


@pytest.mark.mask_smoke
@pytest.mark.skipif(
    os.getenv("RUN_REAL_MASK_TESTS") != "1",
    reason="Real AgnosticMaskGenerator smoke test skipped unless RUN_REAL_MASK_TESTS=1",
)
@pytest.mark.asyncio
async def test_real_mask_generator_smoke_test(sample_input_images, tmp_path: Path):
    """Smoke test for Real SegFormer, Real DWPose, and Real AgnosticMaskGenerator."""
    person_path, garment_path = sample_input_images

    test_settings = Settings(
        AI_PROCESSED_DIR=str(tmp_path / "processed"),
        AI_HUMAN_PARSER_OUTPUT_DIR=str(tmp_path / "processed" / "parsing"),
        AI_POSE_OUTPUT_DIR=str(tmp_path / "processed" / "poses"),
        AI_AGNOSTIC_MASK_OUTPUT_DIR=str(tmp_path / "processed" / "agnostic_masks"),
    )

    pipeline = VirtualWearPipeline(
        preprocessor=ImagePreprocessor(config=test_settings),
        human_parser=SegFormerHumanParser(
            device="cpu",
            output_dir=str(tmp_path / "processed" / "parsing"),
        ),
        pose_estimator=DWPoseEstimator(
            device="cpu",
            detection_threshold=0.00001,
            output_dir=str(tmp_path / "processed" / "poses"),
        ),
        agnostic_mask_generator=AgnosticMaskGenerator(
            output_dir=str(tmp_path / "processed" / "agnostic_masks"),
        ),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    result = await pipeline.run(
        PersonInput(person_id="real_mask_person", image_ref=str(person_path)),
        GarmentInput(
            garment_id="real_mask_garment",
            image_ref=str(garment_path),
            category=GarmentCategory.UPPER_BODY,
        ),
    )

    assert isinstance(result, TryOnResult)
    assert result.final.final_image_id.startswith(
        "final_raw_proc_real_mask_person_proc_real_mask_garment"
    )

    # Verify generated agnostic mask artifact
    mask_dir = tmp_path / "processed" / "agnostic_masks"
    mask_files = list(mask_dir.glob("*.png"))
    assert len(mask_files) == 1
    mask_file = mask_files[0]
    assert mask_file.exists()

    with Image.open(mask_file) as mask_img:
        assert mask_img.format == "PNG"
        assert mask_img.mode == "L"
        assert mask_img.size == (768, 1024)

        mask_arr = np.array(mask_img)
        unique_pixels = set(np.unique(mask_arr))
        assert unique_pixels.issubset({0, 255})
        assert int(np.count_nonzero(mask_arr == 255)) > 0
