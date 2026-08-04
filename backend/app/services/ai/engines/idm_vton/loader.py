import time
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.ai.engines.common.config import VTONEngineConfig
from app.services.ai.engines.common.device_manager import DeviceManager
from app.services.ai.engines.common.exceptions import (
    EngineInitializationError,
    WeightMissingError,
)
from app.services.ai.engines.common.model_weight_manager import ModelWeightManager
from app.utils.logger import logger


class IDMVTONLoader:
    """Loader managing weight verification, component loading, and offloading."""

    def __init__(
        self,
        config: Optional[VTONEngineConfig] = None,
        weight_manager: Optional[ModelWeightManager] = None,
        device_manager: Optional[DeviceManager] = None,
    ) -> None:
        self.config = config or VTONEngineConfig(engine_name="idm_vton")
        self.weight_manager = weight_manager or ModelWeightManager(
            model_dir=self.config.model_directory
        )
        self.device_manager = device_manager or DeviceManager()
        self._components: Optional[Dict[str, Any]] = None
        self._load_duration_ms: float = 0.0

    @property
    def load_duration_ms(self) -> float:
        """Returns the duration of the model loading pass in milliseconds."""
        return self._load_duration_ms

    def load(self, force_reload: bool = False) -> Dict[str, Any]:
        """Verifies weights, resolves device, and loads pipeline components."""
        if self._components is not None and not force_reload:
            return self._components

        start_time = time.perf_counter()
        logger.info(
            f"IDMVTONLoader: Loading engine '{self.config.engine_name}' "
            f"from '{self.config.model_directory}'"
        )

        # 1. Weight Verification
        if not self.weight_manager.verify():
            missing = self.weight_manager.list_missing()
            raise WeightMissingError(
                message=f"Missing weights in '{self.config.model_directory}'",
                missing_assets=missing,
            )

        # 2. Device Resolution
        target_device = self.device_manager.resolve(self.config.device)

        # 3. Construct Components (or STUB if diffusers package / models not loaded)
        try:
            components = self._load_pipeline_modules(target_device)
            self._components = components
            self._load_duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                f"IDMVTONLoader: Loaded IDM-VTON components onto "
                f"device '{target_device}' in {self._load_duration_ms:.2f}ms"
            )
            return self._components
        except Exception as exc:
            logger.error(f"IDMVTONLoader: Failed to load pipeline modules: {exc}")
            raise EngineInitializationError(
                message=f"Failed to construct pipeline modules: {exc}",
                engine_name=self.config.engine_name,
                details=str(exc),
            )

    def _load_pipeline_modules(self, device: str) -> Dict[str, Any]:
        """Loads real diffusers pipeline components or returns mock components if diffusers fails."""
        try:
            import torch
            from diffusers import StableDiffusionXLInpaintPipeline

            target_model_dir = Path(self.config.model_directory)
            if not target_model_dir.exists() and (Path("backend") / target_model_dir).exists():
                target_model_dir = Path("backend") / target_model_dir

            logger.info(
                f"IDMVTONLoader: Instantiating SDXL Inpaint Pipeline from '{target_model_dir}'"
            )
            dtype = torch.float16 if self.config.dtype in ["float16", "fp16"] else torch.float32
            pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
                str(target_model_dir),
                torch_dtype=dtype,
                feature_extractor=None,
                image_encoder=None,
            )

            if device.startswith("cuda") and torch.cuda.is_available():
                pipe.enable_model_cpu_offload()
                if hasattr(pipe, "vae") and hasattr(pipe.vae, "enable_tiling"):
                    pipe.vae.enable_tiling()
                logger.info("IDMVTONLoader: Enabled float16, CPU model offloading, and VAE tiling on GPU")
            elif device != "cpu":
                try:
                    pipe.to(device)
                except Exception as e:
                    logger.warning(f"IDMVTONLoader: pipe.to('{device}') warning: {e}")

            return {
                "device": device,
                "dtype": self.config.dtype,
                "offload_mode": self.config.offload_mode,
                "scheduler": self.config.scheduler,
                "pipe": pipe,
                "mock_fallback": False,
                "unet": getattr(pipe, "unet", "UNet2DConditionModel"),
                "vae": getattr(pipe, "vae", "AutoencoderKL"),
                "text_encoder": getattr(pipe, "text_encoder", "CLIPTextModel"),
                "text_encoder_2": getattr(pipe, "text_encoder_2", "CLIPTextModelWithProjection"),
                "image_encoder": getattr(pipe, "image_encoder", "CLIPVisionModelWithProjection"),
                "config": self.config,
            }
        except Exception as exc:
            logger.warning(f"IDMVTONLoader: Failed to instantiate real diffusers pipeline: {exc}. Falling back to mock component references.")
            return {
                "device": device,
                "dtype": self.config.dtype,
                "offload_mode": self.config.offload_mode,
                "scheduler": self.config.scheduler,
                "mock_fallback": True,
                "unet": "SDXL_Inpaint_UNet",
                "garment_unet": "Garment_UNet",
                "vae": "SDXL_VAE",
                "text_encoder": "CLIPTextModel",
                "text_encoder_2": "OpenCLIPViT_bigG",
                "image_encoder": "CLIPVisionModel",
                "config": self.config,
            }

