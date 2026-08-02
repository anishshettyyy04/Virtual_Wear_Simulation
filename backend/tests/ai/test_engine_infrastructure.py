from pathlib import Path

import pytest

from app.services.ai.engines import (
    ConfigurationError,
    DeviceManager,
    DeviceUnavailableError,
    EngineHealthReport,
    EngineInitializationError,
    InferenceError,
    ModelRegistry,
    ModelWeightManager,
    VTONEngineConfig,
    WeightMissingError,
)
from app.services.ai.exceptions import AIPipelineError


def test_vton_engine_config_defaults() -> None:
    """Verifies VTONEngineConfig default values and serialization."""
    config = VTONEngineConfig()
    assert config.engine_name == "idm_vton"
    assert config.device == "auto"
    assert config.dtype == "fp16"
    assert config.num_inference_steps == 30
    assert config.enable_cpu_offload is True

    custom_config = VTONEngineConfig(
        engine_name="custom_engine",
        num_inference_steps=50,
        guidance_scale=3.5,
    )
    assert custom_config.engine_name == "custom_engine"
    assert custom_config.num_inference_steps == 50
    assert custom_config.guidance_scale == 3.5


def test_engine_health_report_schema() -> None:
    """Verifies EngineHealthReport schema validation and default health states."""
    report = EngineHealthReport(engine_name="idm_vton", is_healthy=True)
    assert report.engine_name == "idm_vton"
    assert report.is_healthy is True
    assert report.model_files_found is False
    assert report.missing_files == []
    assert report.details == {}


def test_device_manager_resolution() -> None:
    """Verifies DeviceManager resolves cpu and auto devices correctly."""
    cpu_device = DeviceManager.resolve("cpu")
    assert cpu_device == "cpu"

    auto_device = DeviceManager.resolve("auto")
    assert auto_device in ("cuda", "cpu", "mps")

    assert DeviceManager.validate("cpu") is True

    desc = DeviceManager.describe()
    assert "cuda_available" in desc
    assert "pytorch_version" in desc


def test_model_registry_operations() -> None:
    """Verifies ModelRegistry registration, discovery, and metadata lookups."""
    registered = ModelRegistry.get_registered_engines()
    assert "idm_vton" in registered
    assert "catvton" in registered

    assert ModelRegistry.is_engine_registered("idm_vton") is True
    info = ModelRegistry.get_engine_info("idm_vton")
    assert info["registered_version"] == "1.0.0"

    ModelRegistry.register_engine("test_engine", metadata={"version": "2.0"})
    assert ModelRegistry.is_engine_registered("test_engine") is True

    with pytest.raises(KeyError):
        ModelRegistry.get_engine_info("unregistered_engine")


def test_model_weight_manager_verification(tmp_path: Path) -> None:
    """Verifies ModelWeightManager file locating, missing reporting, and checksums."""
    req_files = ["unet/model.bin", "vae/model.bin"]
    manager = ModelWeightManager(model_dir=str(tmp_path), required_files=req_files)

    assert manager.verify() is False
    assert len(manager.list_missing()) == 2

    with pytest.raises(WeightMissingError) as exc_info:
        manager.verify(raise_on_missing=True)
    assert exc_info.value.missing_assets == req_files

    # Create dummy files
    (tmp_path / "unet").mkdir(parents=True)
    (tmp_path / "vae").mkdir(parents=True)
    (tmp_path / "unet" / "model.bin").write_text("unet_content")
    (tmp_path / "vae" / "model.bin").write_text("vae_content")

    assert manager.verify() is True
    assert manager.list_missing() == []

    manager.download_stub("yisol/IDM-VTON")


def test_engine_exception_hierarchy() -> None:
    """Verifies engine exceptions inherit properly from AIPipelineError."""
    err_init = EngineInitializationError(
        "Initialization failed", engine_name="idm_vton"
    )
    assert isinstance(err_init, AIPipelineError)
    assert err_init.engine_name == "idm_vton"

    err_weight = WeightMissingError("Missing assets", missing_assets=["unet.bin"])
    assert isinstance(err_weight, AIPipelineError)
    assert err_weight.missing_assets == ["unet.bin"]

    err_inf = InferenceError("CUDA OOM", engine_name="idm_vton")
    assert isinstance(err_inf, AIPipelineError)

    err_dev = DeviceUnavailableError("cuda:1")
    assert isinstance(err_dev, AIPipelineError)
    assert err_dev.requested_device == "cuda:1"

    err_cfg = ConfigurationError("Invalid step count")
    assert isinstance(err_cfg, AIPipelineError)
