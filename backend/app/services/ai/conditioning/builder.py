from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Field

from app.schemas.ai import (
    AgnosticMaskResult,
    ConditioningBundle,
    DensePoseResult,
    GarmentInput,
    HumanParsingResult,
    ImageDimensions,
    PoseEstimationResult,
    PreprocessingResult,
)
from app.services.ai.conditioning.adapters.canonical_mask_adapter import (
    CanonicalMaskAdapter,
)
from app.services.ai.conditioning.adapters.garment_image_adapter import (
    GarmentImageAdapter,
)
from app.services.ai.conditioning.adapters.person_image_adapter import (
    PersonImageAdapter,
)
from app.services.ai.conditioning.base import (
    BaseConditioningAdapter,
    BaseDensePoseService,
)
from app.utils.logger import logger


class EngineCapabilities(BaseModel):
    """Rich capability metadata model for virtual try-on engines."""

    engine_name: str = Field(
        default="generic", json_schema_extra={"example": "idm_vton"}
    )
    engine_version: str = Field(default="1.0.0", json_schema_extra={"example": "1.0.0"})
    requires_densepose: bool = Field(
        default=True, description="Whether engine requires DensePose surface map"
    )
    requires_person_adapter: bool = Field(
        default=True, description="Whether engine requires person image adapter"
    )
    requires_garment_adapter: bool = Field(
        default=True, description="Whether engine requires garment image adapter"
    )
    requires_mask_adapter: bool = Field(
        default=True, description="Whether engine requires mask adapter"
    )
    target_resolution: Tuple[int, int] = Field(
        default=(768, 1024), description="Target (width, height) resolution"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConditioningBuilder(BaseConditioningAdapter):
    """Stateless builder compiling canonical ConditioningBundle instances."""

    def __init__(
        self,
        densepose_service: Optional[BaseDensePoseService] = None,
        person_adapter: Optional[PersonImageAdapter] = None,
        garment_adapter: Optional[GarmentImageAdapter] = None,
        mask_adapter: Optional[CanonicalMaskAdapter] = None,
    ) -> None:
        self.densepose_service = densepose_service
        self.person_adapter = person_adapter or PersonImageAdapter()
        self.garment_adapter = garment_adapter or GarmentImageAdapter()
        self.mask_adapter = mask_adapter or CanonicalMaskAdapter()

    async def prepare(
        self,
        preprocessed: PreprocessingResult,
        parsing: HumanParsingResult,
        pose: PoseEstimationResult,
        agnostic_mask: AgnosticMaskResult,
        garment: GarmentInput,
        densepose: Optional[DensePoseResult] = None,
        capabilities: Optional[EngineCapabilities] = None,
        **kwargs: Any,
    ) -> ConditioningBundle:
        """Prepares a canonical ConditioningBundle based on engine capabilities."""
        caps = capabilities or EngineCapabilities()
        target_w, target_h = caps.target_resolution

        logger.info(
            f"ConditioningBuilder: Preparing bundle for engine '{caps.engine_name}' "
            f"v{caps.engine_version} at ({target_w}x{target_h})"
        )

        available_components = ["person_image", "garment_image", "agnostic_mask"]
        adapter_metadata: Dict[str, Any] = {
            "engine_name": caps.engine_name,
            "engine_version": caps.engine_version,
            "target_resolution": caps.target_resolution,
        }

        # 1. Person Image Adaptation
        if caps.requires_person_adapter:
            adapter_metadata["person_adapter"] = self.person_adapter.adapt(
                preprocessed.person_image_ref, target_resolution=caps.target_resolution
            )

        # 2. Garment Image Adaptation
        if caps.requires_garment_adapter:
            adapter_metadata["garment_adapter"] = self.garment_adapter.adapt(
                preprocessed.garment_image_ref, target_resolution=caps.target_resolution
            )

        # 3. Mask Adaptation
        if caps.requires_mask_adapter:
            adapter_metadata["mask_adapter"] = self.mask_adapter.adapt(
                agnostic_mask.mask_ref, target_resolution=caps.target_resolution
            )

        # 4. DensePose Generation (Conditional)
        dp_result = densepose
        if (
            caps.requires_densepose
            and dp_result is None
            and self.densepose_service is not None
        ):
            logger.info("ConditioningBuilder: Executing DensePose service for bundle")
            dp_result = await self.densepose_service.process(
                preprocessed.person_image_ref
            )

        if dp_result is not None:
            available_components.append("densepose")

        bundle_id = f"bundle_{preprocessed.person_processed_id}"

        person_dims = preprocessed.person_dimensions or ImageDimensions(
            width=target_w, height=target_h
        )
        garment_dims = preprocessed.garment_dimensions or ImageDimensions(
            width=target_w, height=target_h
        )

        return ConditioningBundle(
            bundle_id=bundle_id,
            schema_version="v1",
            conditioning_version="1.0.0",
            person_image_ref=preprocessed.person_image_ref,
            garment_image_ref=preprocessed.garment_image_ref,
            agnostic_mask=agnostic_mask,
            densepose=dp_result,
            garment_category=garment.category,
            person_dimensions=person_dims,
            garment_dimensions=garment_dims,
            available_components=available_components,
            generator_versions={"segformer": "1.0", "dwpose": "1.0"},
            metadata=adapter_metadata,
        )
