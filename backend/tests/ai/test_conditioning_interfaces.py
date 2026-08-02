import pytest

from app.services.ai.conditioning import (
    BaseDensePoseService,
    BaseImageAdapter,
    BaseMaskAdapter,
    DensePoseResult,
    GarmentImageAdapter,
    IDMVTONMaskAdapter,
    MockDensePoseService,
    PersonImageAdapter,
)


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


def test_image_adapter_stubs_raise_not_implemented() -> None:
    """Verifies image adapter stubs raise NotImplementedError on call."""
    person_adapter = PersonImageAdapter()
    garment_adapter = GarmentImageAdapter()

    assert isinstance(person_adapter, BaseImageAdapter)
    assert isinstance(garment_adapter, BaseImageAdapter)

    with pytest.raises(NotImplementedError):
        person_adapter.adapt("test_person.jpg", 768, 1024)

    with pytest.raises(NotImplementedError):
        garment_adapter.adapt("test_garment.jpg", 768, 1024)


def test_mask_adapter_stub_raises_not_implemented() -> None:
    """Verifies mask adapter stub raises NotImplementedError on call."""
    mask_adapter = IDMVTONMaskAdapter()

    assert isinstance(mask_adapter, BaseMaskAdapter)

    with pytest.raises(NotImplementedError):
        mask_adapter.adapt("mask_test.png", 768, 1024)


@pytest.mark.asyncio
async def test_mock_densepose_service_raises_not_implemented() -> None:
    """Verifies mock DensePose service process raises NotImplementedError."""
    service = MockDensePoseService()

    assert isinstance(service, BaseDensePoseService)

    with pytest.raises(NotImplementedError):
        await service.process("person_test.jpg")
