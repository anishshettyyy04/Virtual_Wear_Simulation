from PIL import Image

from app.schemas.ai import AgnosticMaskResult, ConditioningBundle
from app.services.ai.engines.idm_vton.adapters import IDMVTONConditioningAdapter
from app.services.ai.engines.idm_vton.pipeline import IDMVTONPipeline


def test_idm_vton_conditioning_adapter_and_pipeline() -> None:
    """Verifies IDMVTONConditioningAdapter and IDMVTONPipeline execution."""
    mask = AgnosticMaskResult(mask_id="mask_test", mask_ref="mask_test.png")
    bundle = ConditioningBundle(
        bundle_id="bundle_pipe_test",
        person_image_ref="person_test.jpg",
        garment_image_ref="garment_test.jpg",
        agnostic_mask=mask,
    )

    adapter = IDMVTONConditioningAdapter()
    inputs = adapter.prepare_inputs(bundle, target_resolution=(768, 1024))

    assert inputs["bundle_id"] == "bundle_pipe_test"
    assert inputs["person_image"].size == (768, 1024)
    assert inputs["garment_image"].size == (768, 1024)
    assert inputs["agnostic_mask"].size == (768, 1024)

    pipeline = IDMVTONPipeline()
    rendered_img = pipeline.run(inputs, seed=42)

    assert isinstance(rendered_img, Image.Image)
    assert rendered_img.size == (768, 1024)
