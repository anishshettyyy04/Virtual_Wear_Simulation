from pathlib import Path

import pytest

from app.config.settings import Settings
from app.schemas.ai import (
    AgnosticMaskResult,
    GarmentCategory,
    GarmentInput,
    HumanParsingResult,
    PersonInput,
    PoseEstimationResult,
    PreprocessingResult,
)
from app.services.ai.conditioning import (
    CanonicalMaskAdapter,
    ConditioningBuilder,
    DensePoseResult,
    DensePoseService,
    EngineCapabilities,
    GarmentImageAdapter,
    PersonImageAdapter,
)
from app.services.ai.mock.agnostic_mask_generator import MockAgnosticMaskGenerator
from app.services.ai.mock.human_parser import MockHumanParser
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.preprocessor import MockPreprocessor
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.services.ai.pipeline import VirtualWearPipeline


@pytest.mark.asyncio
async def test_densepose_service_placeholder(tmp_path: Path) -> None:
    """Verifies DensePoseService generates deterministic placeholder artifact."""
    custom_settings = Settings(AI_DENSEPOSE_OUTPUT_DIR=str(tmp_path / "densepose"))
    service = DensePoseService(config=custom_settings)

    result = await service.process("test_person.jpg")
    assert isinstance(result, DensePoseResult)
    assert result.densepose_id.startswith("dp_test_person")
    assert Path(result.densepose_ref).exists()
    assert result.metadata["implementation"] == "placeholder"
    assert result.metadata["provider"] == "mock_densepose"
    assert result.metadata["schema_version"] == "v1"


def test_person_and_garment_image_adapters() -> None:
    """Verifies PersonImageAdapter and GarmentImageAdapter adaptation metadata."""
    person_adapter = PersonImageAdapter()
    garment_adapter = GarmentImageAdapter()

    p_meta = person_adapter.adapt("person.jpg", target_resolution=(768, 1024))
    assert p_meta["target_resolution"] == (768, 1024)
    assert p_meta["adapter"] == "PersonImageAdapter"

    g_meta = garment_adapter.adapt("garment.jpg", target_resolution=(768, 1024))
    assert g_meta["target_resolution"] == (768, 1024)
    assert g_meta["background_fill"] == "white"

    with pytest.raises(ValueError):
        person_adapter.adapt("", target_resolution=(768, 1024))


def test_canonical_mask_adapter() -> None:
    """Verifies CanonicalMaskAdapter metadata and mask inspection."""
    mask_adapter = CanonicalMaskAdapter()
    m_meta = mask_adapter.adapt("mask.png", target_resolution=(768, 1024))

    assert m_meta["target_resolution"] == (768, 1024)
    assert m_meta["adapter"] == "CanonicalMaskAdapter"
    assert m_meta["polarity"] == "0=preserve, 255=inpaint_hole"

    with pytest.raises(ValueError):
        mask_adapter.adapt("", target_resolution=(768, 1024))


@pytest.mark.asyncio
async def test_conditioning_builder_with_densepose(tmp_path: Path) -> None:
    """Verifies ConditioningBuilder executes DensePoseService when required."""
    custom_settings = Settings(AI_DENSEPOSE_OUTPUT_DIR=str(tmp_path / "dp"))
    dp_service = DensePoseService(config=custom_settings)
    builder = ConditioningBuilder(densepose_service=dp_service)

    preprocessed = PreprocessingResult(
        person_processed_id="proc_p1",
        person_image_ref="proc_p1.jpg",
        garment_processed_id="proc_g1",
        garment_image_ref="proc_g1.jpg",
    )
    parsing = HumanParsingResult(mask_id="mask_p1")
    pose = PoseEstimationResult(pose_id="pose_p1")
    agnostic_mask = AgnosticMaskResult(mask_id="ag_p1", mask_ref="ag_p1.png")
    garment = GarmentInput(garment_id="g1", image_ref="g1.jpg")

    caps = EngineCapabilities(
        engine_name="idm_vton",
        engine_version="1.0.0",
        requires_densepose=True,
        target_resolution=(768, 1024),
    )

    bundle = await builder.prepare(
        preprocessed, parsing, pose, agnostic_mask, garment, capabilities=caps
    )

    assert bundle.bundle_id == "bundle_proc_p1"
    assert bundle.densepose is not None
    assert bundle.densepose.metadata["provider"] == "mock_densepose"
    assert "densepose" in bundle.available_components
    assert bundle.metadata["engine_name"] == "idm_vton"


@pytest.mark.asyncio
async def test_conditioning_builder_without_densepose(tmp_path: Path) -> None:
    """Verifies ConditioningBuilder skips DensePose when requires_densepose=False."""
    custom_settings = Settings(AI_DENSEPOSE_OUTPUT_DIR=str(tmp_path / "dp"))
    dp_service = DensePoseService(config=custom_settings)
    builder = ConditioningBuilder(densepose_service=dp_service)

    preprocessed = PreprocessingResult(
        person_processed_id="proc_p2",
        person_image_ref="proc_p2.jpg",
        garment_processed_id="proc_g2",
        garment_image_ref="proc_g2.jpg",
    )
    parsing = HumanParsingResult(mask_id="mask_p2")
    pose = PoseEstimationResult(pose_id="pose_p2")
    agnostic_mask = AgnosticMaskResult(mask_id="ag_p2", mask_ref="ag_p2.png")
    garment = GarmentInput(garment_id="g2", image_ref="g2.jpg")

    caps = EngineCapabilities(
        engine_name="cat_vton",
        requires_densepose=False,
    )

    bundle = await builder.prepare(
        preprocessed, parsing, pose, agnostic_mask, garment, capabilities=caps
    )

    assert bundle.densepose is None
    assert "densepose" not in bundle.available_components
    assert bundle.metadata["engine_name"] == "cat_vton"


@pytest.mark.asyncio
async def test_pipeline_integration_with_conditioning_builder(tmp_path: Path) -> None:
    """Verifies end-to-end pipeline execution with real ConditioningBuilder."""
    custom_settings = Settings(AI_DENSEPOSE_OUTPUT_DIR=str(tmp_path / "dp"))
    builder = ConditioningBuilder(
        densepose_service=DensePoseService(config=custom_settings)
    )

    pipeline = VirtualWearPipeline(
        preprocessor=MockPreprocessor(),
        human_parser=MockHumanParser(),
        pose_estimator=MockPoseEstimator(),
        agnostic_mask_generator=MockAgnosticMaskGenerator(),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
        conditioning_adapter=builder,
    )

    person = PersonInput(person_id="p_int", image_ref="avatars/p_int.jpg")
    garment = GarmentInput(
        garment_id="g_int",
        image_ref="garments/g_int.jpg",
        category=GarmentCategory.UPPER_BODY,
    )

    result = await pipeline.run(person, garment)
    assert result.final.final_image_id is not None
    assert result.pipeline_metadata["conditioning_bundle_id"] == "bundle_proc_p_int"
