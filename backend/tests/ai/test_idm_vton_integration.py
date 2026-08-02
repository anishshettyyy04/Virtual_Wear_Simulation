import os
from pathlib import Path

import pytest
from PIL import Image

from app.schemas.ai import (
    GarmentCategory,
    GarmentInput,
    PersonInput,
)
from app.services.ai.conditioning import ConditioningBuilder
from app.services.ai.engines.idm_vton import IDMVTONEngine
from app.services.ai.mock.agnostic_mask_generator import MockAgnosticMaskGenerator
from app.services.ai.mock.human_parser import MockHumanParser
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.preprocessor import MockPreprocessor
from app.services.ai.pipeline import VirtualWearPipeline


@pytest.mark.asyncio
async def test_virtual_wear_pipeline_with_real_idm_vton_engine(tmp_path: Path) -> None:
    """Verifies VirtualWearPipeline integration using IDMVTONEngine."""
    engine = IDMVTONEngine()
    builder = ConditioningBuilder()

    pipeline = VirtualWearPipeline(
        preprocessor=MockPreprocessor(),
        human_parser=MockHumanParser(),
        pose_estimator=MockPoseEstimator(),
        agnostic_mask_generator=MockAgnosticMaskGenerator(),
        tryon_engine=engine,
        postprocessor=MockPostprocessor(),
        conditioning_adapter=builder,
    )

    person = PersonInput(person_id="p_vton", image_ref="avatars/p_vton.jpg")
    garment = GarmentInput(
        garment_id="g_vton",
        image_ref="garments/g_vton.jpg",
        category=GarmentCategory.UPPER_BODY,
    )

    result = await pipeline.run(person, garment)
    assert result.final.final_image_id is not None
    assert "conditioning_bundle_id" in result.pipeline_metadata


@pytest.mark.vton_smoke
@pytest.mark.skipif(
    os.getenv("RUN_REAL_VTON_TESTS") != "1",
    reason="Real IDM-VTON smoke test disabled unless RUN_REAL_VTON_TESTS=1",
)
@pytest.mark.asyncio
async def test_idm_vton_smoke_test() -> None:
    """Smoke test executing full IDM-VTON model inference when RUN_REAL_VTON_TESTS=1."""
    engine = IDMVTONEngine()
    health = await engine.check_health()
    if not health.model_files_found:
        pytest.skip("IDM-VTON model weights not found locally.")

    person = PersonInput(person_id="p_smoke", image_ref="avatars/p_smoke.jpg")
    garment = GarmentInput(
        garment_id="g_smoke",
        image_ref="garments/g_smoke.jpg",
        category=GarmentCategory.UPPER_BODY,
    )

    pipeline = VirtualWearPipeline(
        preprocessor=MockPreprocessor(),
        human_parser=MockHumanParser(),
        pose_estimator=MockPoseEstimator(),
        agnostic_mask_generator=MockAgnosticMaskGenerator(),
        tryon_engine=engine,
        postprocessor=MockPostprocessor(),
        conditioning_adapter=ConditioningBuilder(),
    )

    result = await pipeline.run(person, garment)
    assert result.final.final_image_id is not None

    output_path = Path(result.final.final_image_ref)
    assert output_path.exists()
    assert output_path.stat().st_size > 0

    with Image.open(output_path) as img:
        assert img.width > 0
        assert img.height > 0
