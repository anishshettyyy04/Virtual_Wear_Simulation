from pathlib import Path

import pytest

from app.services.ai.engines import VTONEngineConfig, WeightMissingError
from app.services.ai.engines.common.model_weight_manager import ModelWeightManager
from app.services.ai.engines.idm_vton.loader import IDMVTONLoader


def test_idm_vton_loader_missing_weights(tmp_path: Path) -> None:
    """Verifies loader raises WeightMissingError when weights are missing."""
    config = VTONEngineConfig(model_directory=str(tmp_path / "missing_vton"))
    wm = ModelWeightManager(model_dir=str(tmp_path / "missing_vton"))
    loader = IDMVTONLoader(config=config, weight_manager=wm)

    with pytest.raises(WeightMissingError) as exc_info:
        loader.load()
    assert "missing" in str(exc_info.value).lower()


def test_idm_vton_loader_successful_stub_load(tmp_path: Path) -> None:
    """Verifies loader returns components when weight files exist."""
    model_dir = tmp_path / "vton_weights"
    model_dir.mkdir()
    wm = ModelWeightManager(
        model_dir=str(model_dir),
        required_files=["unet/model.bin"],
    )
    (model_dir / "unet").mkdir()
    (model_dir / "unet" / "model.bin").write_text("dummy")

    config = VTONEngineConfig(model_directory=str(model_dir))
    loader = IDMVTONLoader(config=config, weight_manager=wm)

    components = loader.load()
    assert components["unet"] == "SDXL_Inpaint_UNet"
    assert components["dtype"] == "fp16"
    assert loader.load_duration_ms > 0.0
