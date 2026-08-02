from pathlib import Path

import pytest
from PIL import Image

from app.schemas.ai import AgnosticMaskResult, ConditioningBundle
from app.services.ai.engines.common import (
    InferenceMetrics,
    ModelWeightManager,
)
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.services.ai.storage import ArtifactStorage


def test_inference_metrics_schema() -> None:
    """Verifies InferenceMetrics schema instantiation and serialization."""
    metrics = InferenceMetrics(
        inference_time_ms=1250.5,
        preprocessing_time_ms=15.0,
        loading_time_ms=50.0,
        total_time_ms=1315.5,
        device="cuda",
        dtype="fp16",
        scheduler="ddpm",
        inference_steps=30,
        guidance_scale=2.0,
        peak_memory_mb=4200.5,
    )
    assert metrics.inference_time_ms == 1250.5
    assert metrics.device == "cuda"
    assert metrics.dtype == "fp16"
    assert metrics.peak_memory_mb == 4200.5
    m_dict = metrics.model_dump()
    assert m_dict["total_time_ms"] == 1315.5


def test_artifact_storage_operations(tmp_path: Path) -> None:
    """Verifies ArtifactStorage naming, atomic saving, and metadata creation."""
    storage = ArtifactStorage(base_output_dir=str(tmp_path))

    art_id, filename = storage.generate_artifact_id("test", "avatars/user.jpg")
    assert art_id.startswith("test_user_")
    assert filename == f"{art_id}.png"

    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    saved_path = storage.save_image_atomically(
        image=img, output_dir=tmp_path / "out", filename=filename
    )
    assert Path(saved_path).exists()

    meta = storage.create_metadata(
        artifact_id=art_id,
        file_path=saved_path,
        artifact_type="tryon_render",
        dimensions=(100, 100),
    )
    assert meta["artifact_id"] == art_id
    assert meta["width"] == 100
    assert meta["height"] == 100


def test_model_weight_manager_revision_tracking(tmp_path: Path) -> None:
    """Verifies ModelWeightManager revision metadata tracking."""
    manager = ModelWeightManager(
        model_dir=str(tmp_path),
        model_revision="v1.0-official",
        source_repository="yisol/IDM-VTON",
    )
    rev_meta = manager.get_revision_metadata()
    assert rev_meta["model_revision"] == "v1.0-official"
    assert rev_meta["source_repository"] == "yisol/IDM-VTON"
    assert rev_meta["verification_status"] == "unverified"


@pytest.mark.asyncio
async def test_mock_engine_warmup_and_metrics() -> None:
    """Verifies engine warmup hook and standardized metadata on RawTryOnOutput."""
    engine = MockTryOnEngine()
    await engine.warmup()

    mask = AgnosticMaskResult(mask_id="m1", mask_ref="m1.png")
    bundle = ConditioningBundle(
        bundle_id="b1",
        person_image_ref="p1.jpg",
        garment_image_ref="g1.jpg",
        agnostic_mask=mask,
    )
    output = await engine.generate(conditioning=bundle)
    assert output.metadata["engine"] == "mock_vton"
    assert "metrics" in output.metadata
    assert output.metadata["metrics"]["total_time_ms"] == 165.0
