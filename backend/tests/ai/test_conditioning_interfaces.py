import pytest

from app.schemas.ai import (
    AgnosticMaskResult,
    ConditioningBundle,
    DensePoseResult,
    GarmentCategory,
    GarmentInput,
    ImageDimensions,
    PersonInput,
)
from app.services.ai.conditioning import (
    BaseDensePoseService,
    BaseImageAdapter,
    BaseMaskAdapter,
    GarmentImageAdapter,
    IDMVTONMaskAdapter,
    MockDensePoseService,
    PersonImageAdapter,
)
from app.services.ai.mock.agnostic_mask_generator import MockAgnosticMaskGenerator
from app.services.ai.mock.human_parser import MockHumanParser
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.preprocessor import MockPreprocessor
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.services.ai.pipeline import VirtualWearPipeline


def test_densepose_result_schema() -> None:
    """Verifies DensePoseResult schema validation and default metadata dict."""
    result = DensePoseResult(
        densepose_id="dp_test_123",
        densepose_ref="data/processed/densepose/dp_test_123.png",
        height=1024,
        width=768,
    )
    assert result.densepose_id == "dp_test_123"
    assert result.densepose_ref == "data/processed/densepose/dp_test_123.png"
    assert result.height == 1024
    assert result.width == 768
    assert result.metadata == {}


def test_conditioning_bundle_construction_without_densepose() -> None:
    """Verifies ConditioningBundle construction without optional DensePoseResult."""
    mask = AgnosticMaskResult(
        mask_id="mask_001",
        mask_ref="data/processed/masks/mask_001.png",
        garment_category="upper_body",
        replace_coverage=0.3,
    )
    bundle = ConditioningBundle(
        bundle_id="bundle_001",
        person_image_ref="data/processed/person_001.png",
        garment_image_ref="data/processed/garment_001.png",
        agnostic_mask=mask,
        garment_category=GarmentCategory.UPPER_BODY,
        person_dimensions=ImageDimensions(width=768, height=1024),
        garment_dimensions=ImageDimensions(width=768, height=1024),
        available_components=["person_image", "garment_image", "agnostic_mask"],
        generator_versions={"segformer": "1.0.0", "dwpose": "1.0.0"},
        metadata={"custom_flag": True},
    )
    assert bundle.bundle_id == "bundle_001"
    assert bundle.schema_version == "v1"
    assert bundle.conditioning_version == "1.0.0"
    assert bundle.densepose is None
    assert bundle.garment_category == GarmentCategory.UPPER_BODY
    assert bundle.person_dimensions.width == 768
    assert bundle.available_components == [
        "person_image",
        "garment_image",
        "agnostic_mask",
    ]
    assert bundle.metadata["custom_flag"] is True


def test_conditioning_bundle_construction_with_densepose() -> None:
    """Verifies ConditioningBundle construction with optional DensePoseResult."""
    mask = AgnosticMaskResult(
        mask_id="mask_002",
        mask_ref="data/processed/masks/mask_002.png",
    )
    densepose = DensePoseResult(
        densepose_id="dp_002",
        densepose_ref="data/processed/densepose/dp_002.png",
        height=1024,
        width=768,
    )
    bundle = ConditioningBundle(
        bundle_id="bundle_002",
        person_image_ref="data/processed/person_002.png",
        garment_image_ref="data/processed/garment_002.png",
        agnostic_mask=mask,
        densepose=densepose,
        garment_category="upper_body",
    )
    assert bundle.bundle_id == "bundle_002"
    assert bundle.densepose is not None
    assert bundle.densepose.densepose_id == "dp_002"
    assert bundle.densepose.densepose_ref == "data/processed/densepose/dp_002.png"


def test_conditioning_bundle_metadata_serialization() -> None:
    """Verifies metadata serialization to python dict and JSON string."""
    mask = AgnosticMaskResult(
        mask_id="mask_003",
        mask_ref="data/processed/masks/mask_003.png",
    )
    bundle = ConditioningBundle(
        bundle_id="bundle_003",
        person_image_ref="data/processed/person_003.png",
        garment_image_ref="data/processed/garment_003.png",
        agnostic_mask=mask,
        metadata={"pipeline": "virtual_wear_v1"},
    )
    bundle_dict = bundle.model_dump()
    assert bundle_dict["bundle_id"] == "bundle_003"
    assert bundle_dict["metadata"]["pipeline"] == "virtual_wear_v1"

    bundle_json = bundle.model_dump_json()
    assert (
        '"bundle_id":"bundle_003"' in bundle_json
        or '"bundle_id": "bundle_003"' in bundle_json
    )


@pytest.mark.asyncio
async def test_mock_tryon_engine_with_conditioning_bundle() -> None:
    """Verifies MockTryOnEngine accepts ConditioningBundle."""
    engine = MockTryOnEngine()
    mask = AgnosticMaskResult(
        mask_id="mask_004",
        mask_ref="data/processed/masks/mask_004.png",
    )
    bundle = ConditioningBundle(
        bundle_id="bundle_004",
        person_image_ref="data/processed/person_004.png",
        garment_image_ref="data/processed/garment_004.png",
        agnostic_mask=mask,
    )
    raw_output = await engine.generate(conditioning=bundle)
    assert raw_output.raw_render_id == "raw_bundle_004"
    assert raw_output.output_ref == "mock://renders/raw_bundle_004.png"
    assert raw_output.metadata["agnostic_mask_id"] == "mask_004"


@pytest.mark.asyncio
async def test_pipeline_execution_with_conditioning_bundle() -> None:
    """Verifies VirtualWearPipeline executes generating ConditioningBundle."""
    pipeline = VirtualWearPipeline(
        preprocessor=MockPreprocessor(),
        human_parser=MockHumanParser(),
        pose_estimator=MockPoseEstimator(),
        agnostic_mask_generator=MockAgnosticMaskGenerator(),
        tryon_engine=MockTryOnEngine(),
        postprocessor=MockPostprocessor(),
    )
    person = PersonInput(person_id="p123", image_ref="avatars/p123.jpg")
    garment = GarmentInput(
        garment_id="g456",
        image_ref="garments/g456.jpg",
        category=GarmentCategory.UPPER_BODY,
    )
    result = await pipeline.run(person, garment)
    assert result.final.final_image_id is not None
    assert "conditioning_bundle_id" in result.pipeline_metadata
    assert result.pipeline_metadata["conditioning_bundle_id"] == "bundle_proc_p123"


def test_image_adapters_working_execution() -> None:
    """Verifies image adapters return valid adaptation metadata."""
    person_adapter = PersonImageAdapter()
    garment_adapter = GarmentImageAdapter()

    assert isinstance(person_adapter, BaseImageAdapter)
    assert isinstance(garment_adapter, BaseImageAdapter)

    p_res = person_adapter.adapt("test_person.jpg", target_resolution=(768, 1024))
    g_res = garment_adapter.adapt("test_garment.jpg", target_resolution=(768, 1024))

    assert p_res["target_resolution"] == (768, 1024)
    assert g_res["target_resolution"] == (768, 1024)


def test_mask_adapter_working_execution() -> None:
    """Verifies mask adapter returns valid adaptation metadata."""
    mask_adapter = IDMVTONMaskAdapter()

    assert isinstance(mask_adapter, BaseMaskAdapter)

    m_res = mask_adapter.adapt("mask_test.png", target_resolution=(768, 1024))
    assert m_res["target_resolution"] == (768, 1024)


@pytest.mark.asyncio
async def test_mock_densepose_service_working_execution() -> None:
    """Verifies MockDensePoseService produces valid DensePoseResult."""
    service = MockDensePoseService()

    assert isinstance(service, BaseDensePoseService)

    result = await service.process("person_test.jpg")
    assert isinstance(result, DensePoseResult)
    assert result.densepose_id.startswith("dp_person_test")
