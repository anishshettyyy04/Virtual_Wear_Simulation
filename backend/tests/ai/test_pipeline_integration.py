from pathlib import Path

import pytest
from PIL import Image

from app.config.settings import Settings
from app.schemas.ai import GarmentInput, PersonInput, TryOnResult
from app.services.ai.mock.human_parser import MockHumanParser
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.services.ai.pipeline import VirtualWearPipeline
from app.services.ai.preprocessing.image_preprocessor import ImagePreprocessor


def create_test_image(path: Path, width: int, height: int, fmt: str = "JPEG") -> Path:
    """Helper creating temporary test images."""
    img = Image.new("RGB", (width, height), (0, 255, 0))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format=fmt)
    return path


@pytest.mark.asyncio
async def test_pipeline_integration_real_preprocessor(tmp_path: Path) -> None:
    """Verifies VirtualWearPipeline runs successfully with real ImagePreprocessor."""
    p_path = create_test_image(tmp_path / "avatar.jpg", 1500, 1000)
    g_path = create_test_image(tmp_path / "shirt.png", 800, 800, fmt="PNG")

    custom_settings = Settings(
        AI_PROCESSED_DIR=str(tmp_path / "data" / "processed"),
        AI_PREPROCESS_MAX_WIDTH=1024,
        AI_PREPROCESS_MAX_HEIGHT=1024,
    )

    real_preprocessor = ImagePreprocessor(config=custom_settings)

    pipeline = VirtualWearPipeline(
        preprocessor=real_preprocessor,
        human_parser=MockHumanParser(),
        pose_estimator=MockPoseEstimator(),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )

    person = PersonInput(person_id="user_123", image_ref=str(p_path))
    garment = GarmentInput(
        garment_id="shirt_456", image_ref=str(g_path), category="upper_body"
    )

    result = await pipeline.run(person, garment)

    assert isinstance(result, TryOnResult)
    assert result.final.final_image_id.startswith(
        "final_raw_proc_user_123_proc_shirt_456"
    )
    assert result.pipeline_metadata["model_name"] == "mock"
    assert result.pipeline_metadata["confidence_score"] == 0.95
