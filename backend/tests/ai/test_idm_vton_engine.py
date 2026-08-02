from pathlib import Path

import pytest

from app.schemas.ai import AgnosticMaskResult, ConditioningBundle, RawTryOnOutput
from app.services.ai.engines import VTONEngineConfig
from app.services.ai.engines.idm_vton import IDMVTONEngine
from app.services.ai.storage import ArtifactStorage


@pytest.mark.asyncio
async def test_idm_vton_engine_lifecycle(tmp_path: Path) -> None:
    """Verifies IDMVTONEngine health check, lazy init, warmup, and shutdown."""
    config = VTONEngineConfig(model_directory=str(tmp_path / "vton_dir"))
    storage = ArtifactStorage(base_output_dir=str(tmp_path / "renders"))

    engine = IDMVTONEngine(config=config, artifact_storage=storage)

    # 1. Health check
    health = await engine.check_health()
    assert health.engine_name == "idm_vton"

    # 2. Warmup & Lazy Init
    await engine.warmup()
    assert engine._initialized is True

    # 3. Generate
    mask = AgnosticMaskResult(mask_id="m_eng", mask_ref="m_eng.png")
    bundle = ConditioningBundle(
        bundle_id="b_eng",
        person_image_ref="p_eng.jpg",
        garment_image_ref="g_eng.jpg",
        agnostic_mask=mask,
    )

    output = await engine.generate(conditioning=bundle, seed=123)
    assert isinstance(output, RawTryOnOutput)
    assert output.model_name == "idm_vton"
    assert Path(output.output_ref).exists()
    assert output.metadata["engine"] == "idm_vton"
    assert "metrics" in output.metadata

    # 4. Shutdown
    await engine.shutdown()
    assert engine._initialized is False
