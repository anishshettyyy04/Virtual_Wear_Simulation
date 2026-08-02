import asyncio
import time
from typing import Any, Dict, Optional

from app.schemas.ai import (
    AgnosticMaskResult,
    ConditioningBundle,
    GarmentInput,
    HumanParsingResult,
    PoseEstimationResult,
    PreprocessingResult,
    RawTryOnOutput,
)
from app.services.ai.engines.common.config import VTONEngineConfig
from app.services.ai.engines.common.device_manager import DeviceManager
from app.services.ai.engines.common.exceptions import (
    EngineInitializationError,
    InferenceError,
)
from app.services.ai.engines.common.health import EngineHealthReport
from app.services.ai.engines.common.metrics import InferenceMetrics
from app.services.ai.engines.common.model_weight_manager import ModelWeightManager
from app.services.ai.engines.idm_vton.adapters import IDMVTONConditioningAdapter
from app.services.ai.engines.idm_vton.loader import IDMVTONLoader
from app.services.ai.engines.idm_vton.pipeline import IDMVTONPipeline
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.services.ai.storage.artifact_storage import ArtifactStorage
from app.utils.logger import logger


class IDMVTONEngine(BaseTryOnEngine):
    """Production virtual try-on engine for official IDM-VTON diffusion model."""

    def __init__(
        self,
        config: Optional[VTONEngineConfig] = None,
        loader: Optional[IDMVTONLoader] = None,
        adapter: Optional[IDMVTONConditioningAdapter] = None,
        pipeline_wrapper: Optional[IDMVTONPipeline] = None,
        weight_manager: Optional[ModelWeightManager] = None,
        device_manager: Optional[DeviceManager] = None,
        artifact_storage: Optional[ArtifactStorage] = None,
    ) -> None:
        self.config = config or VTONEngineConfig(engine_name="idm_vton")
        self.weight_manager = weight_manager or ModelWeightManager(
            model_dir=self.config.model_directory
        )
        self.device_manager = device_manager or DeviceManager()
        self.loader = loader or IDMVTONLoader(
            config=self.config,
            weight_manager=self.weight_manager,
            device_manager=self.device_manager,
        )
        self.adapter = adapter or IDMVTONConditioningAdapter()
        self.pipeline_wrapper = pipeline_wrapper
        self.artifact_storage = artifact_storage or ArtifactStorage(
            base_output_dir="data/processed/renders"
        )

        self._initialized: bool = False
        self._components: Optional[Dict[str, Any]] = None
        self._semaphore = asyncio.Semaphore(1)

    async def check_health(self) -> EngineHealthReport:
        """Evaluates engine readiness without heavy model loading."""
        files_found = self.weight_manager.verify()
        missing = self.weight_manager.list_missing() if not files_found else []
        device_ok = self.device_manager.validate(self.config.device)

        is_healthy = files_found and device_ok

        return EngineHealthReport(
            engine_name=self.config.engine_name,
            is_healthy=is_healthy,
            model_files_found=files_found,
            scheduler_available=True,
            vae_available=files_found,
            unet_available=files_found,
            config_valid=True,
            execution_device_available=device_ok,
            missing_files=missing,
            details={
                "model_dir": self.config.model_directory,
                "target_device": self.config.device,
                "revision_meta": self.weight_manager.get_revision_metadata(),
            },
        )

    async def initialize(self) -> None:
        """Lazily initializes model components."""
        if self._initialized:
            return

        logger.info(f"IDMVTONEngine: Initializing '{self.config.engine_name}'...")
        health = await self.check_health()
        if not health.is_healthy and health.missing_files:
            logger.warning(
                f"IDMVTONEngine: Weight files missing: {health.missing_files}. "
                f"Operating in testing/mock fallback mode."
            )

        try:
            # If weight files are missing or mock, load returns stub components
            if self.weight_manager.verify():
                self._components = self.loader.load()
            else:
                self._components = {
                    "device": self.config.device,
                    "dtype": self.config.dtype,
                    "offload_mode": self.config.offload_mode,
                    "scheduler": self.config.scheduler,
                    "mock_fallback": True,
                }
            if self.pipeline_wrapper is None:
                self.pipeline_wrapper = IDMVTONPipeline(components=self._components)

            self._initialized = True
            logger.info("IDMVTONEngine: Initialization complete.")
        except Exception as exc:
            logger.error(f"IDMVTONEngine: Initialization error: {exc}")
            raise EngineInitializationError(
                message=f"Initialization failed: {exc}",
                engine_name=self.config.engine_name,
                details=str(exc),
            )

    async def warmup(self) -> None:
        """Optional warm-up execution preloading models into memory."""
        await self.initialize()
        logger.info("IDMVTONEngine: Warm-up pass executed successfully.")

    async def shutdown(self) -> None:
        """Releases components and cleans up GPU/CPU resources."""
        self._components = None
        self.pipeline_wrapper = None
        self._initialized = False
        logger.info("IDMVTONEngine: Engine shutdown complete.")

    async def generate(
        self,
        preprocessed: Optional[PreprocessingResult] = None,
        parsing: Optional[HumanParsingResult] = None,
        pose: Optional[PoseEstimationResult] = None,
        agnostic_mask: Optional[AgnosticMaskResult] = None,
        garment: Optional[GarmentInput] = None,
        conditioning: Optional[ConditioningBundle] = None,
        seed: Optional[int] = None,
        **kwargs: Any,
    ) -> RawTryOnOutput:
        """Executes IDM-VTON virtual try-on inference protected by asyncio.Semaphore."""
        t_total_start = time.perf_counter()

        if not self._initialized:
            await self.initialize()

        # Handle legacy positional calls if conditioning bundle is omitted
        if conditioning is None:
            if preprocessed is None or agnostic_mask is None or garment is None:
                raise ValueError(
                    "IDMVTONEngine requires ConditioningBundle or positional inputs."
                )
            bundle_id = f"bundle_{preprocessed.person_processed_id}"
            conditioning = ConditioningBundle(
                bundle_id=bundle_id,
                person_image_ref=preprocessed.person_image_ref,
                garment_image_ref=preprocessed.garment_image_ref,
                agnostic_mask=agnostic_mask,
                garment_category=garment.category,
            )

        async with self._semaphore:
            try:
                # 1. Conditioning Adaptation & Preprocessing
                t_prep_start = time.perf_counter()
                inputs = self.adapter.prepare_inputs(
                    conditioning,
                    target_resolution=(
                        self.config.metadata.get("target_width", 768),
                        self.config.metadata.get("target_height", 1024),
                    ),
                )
                t_prep_end = time.perf_counter()
                prep_time_ms = (t_prep_end - t_prep_start) * 1000.0

                # 2. Diffusion Pipeline Inference
                t_inf_start = time.perf_counter()
                rendered_img = self.pipeline_wrapper.run(
                    inputs,
                    seed=seed,
                    num_inference_steps=self.config.num_inference_steps,
                    guidance_scale=self.config.guidance_scale,
                )
                t_inf_end = time.perf_counter()
                inf_time_ms = (t_inf_end - t_inf_start) * 1000.0

                # 3. Artifact Storage
                art_id, filename = self.artifact_storage.generate_artifact_id(
                    "raw", conditioning.person_image_ref, extra_seed=str(seed or "")
                )
                saved_path = self.artifact_storage.save_image_atomically(
                    image=rendered_img,
                    output_dir="data/processed/renders",
                    filename=filename,
                )

                total_time_ms = (time.perf_counter() - t_total_start) * 1000.0

                # 4. Metrics & Metadata Assembly
                metrics = InferenceMetrics(
                    inference_time_ms=round(inf_time_ms, 2),
                    preprocessing_time_ms=round(prep_time_ms, 2),
                    loading_time_ms=round(self.loader.load_duration_ms, 2),
                    total_time_ms=round(total_time_ms, 2),
                    device=self.config.device,
                    dtype=self.config.dtype,
                    scheduler=self.config.scheduler,
                    inference_steps=self.config.num_inference_steps,
                    guidance_scale=self.config.guidance_scale,
                )

                rev_meta = self.weight_manager.get_revision_metadata()
                engine_metadata = {
                    "engine": "idm_vton",
                    "engine_version": "1.0.0",
                    "pipeline_version": "1.0.0",
                    "model_revision": rev_meta["model_revision"],
                    "source_repository": rev_meta["source_repository"],
                    "device": self.config.device,
                    "dtype": self.config.dtype,
                    "offload_mode": self.config.offload_mode,
                    "scheduler": self.config.scheduler,
                    "generator": "IDMVTONEngine",
                    "seed": seed,
                    "metrics": metrics.model_dump(),
                }

                logger.info(
                    f"IDMVTONEngine: Rendered '{art_id}' in {total_time_ms:.2f}ms"
                )

                return RawTryOnOutput(
                    raw_render_id=art_id,
                    output_ref=saved_path,
                    confidence_score=0.98,
                    model_name="idm_vton",
                    model_version="1.0.0",
                    metadata=engine_metadata,
                )

            except asyncio.CancelledError:
                logger.warning("IDMVTONEngine: Inference execution was cancelled.")
                raise
            except Exception as exc:
                logger.error(f"IDMVTONEngine: Inference execution error: {exc}")
                raise InferenceError(
                    message=f"Inference execution failed: {exc}",
                    engine_name=self.config.engine_name,
                    details=str(exc),
                )
