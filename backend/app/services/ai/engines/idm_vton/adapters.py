import os
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
from PIL import Image

from app.schemas.ai import ConditioningBundle
from app.utils.logger import logger


class IDMVTONConditioningAdapter:
    """Adapts canonical ConditioningBundle artifacts into IDM-VTON engine inputs."""

    def prepare_inputs(
        self,
        conditioning: ConditioningBundle,
        target_resolution: Tuple[int, int] = (768, 1024),
    ) -> Dict[str, Any]:
        """Validates and prepares PIL images and tensor inputs for IDM-VTON."""
        target_w, target_h = target_resolution
        logger.info(
            f"IDMVTONConditioningAdapter: Inputs for '{conditioning.bundle_id}' "
            f"at ({target_w}x{target_h})"
        )

        # 1. Person Image
        person_img = self._load_and_resize_image(
            conditioning.person_image_ref, (target_w, target_h), mode="RGB"
        )

        # 2. Garment Image
        garment_img = self._load_and_resize_image(
            conditioning.garment_image_ref, (target_w, target_h), mode="RGB"
        )

        # 3. Agnostic Mask
        mask_ref = conditioning.agnostic_mask.mask_ref
        mask_img = self._load_and_resize_image(mask_ref, (target_w, target_h), mode="L")

        # 4. DensePose (Optional surface map)
        densepose_img = None
        if conditioning.densepose and conditioning.densepose.densepose_ref:
            dp_ref = conditioning.densepose.densepose_ref
            if os.path.exists(dp_ref):
                densepose_img = self._load_and_resize_image(
                    dp_ref, (target_w, target_h), mode="RGB"
                )

        if densepose_img is None:
            # Fallback placeholder RGB surface map
            densepose_img = Image.new("RGB", (target_w, target_h), color=(30, 144, 255))

        return {
            "bundle_id": conditioning.bundle_id,
            "person_image": person_img,
            "garment_image": garment_img,
            "agnostic_mask": mask_img,
            "densepose_image": densepose_img,
            "garment_category": str(conditioning.garment_category),
            "target_resolution": (target_w, target_h),
            "metadata": conditioning.metadata,
        }

    def _load_and_resize_image(
        self, image_ref: str, resolution: Tuple[int, int], mode: str = "RGB"
    ) -> Image.Image:
        """Helper loading and resizing an image artifact to target resolution."""
        target_w, target_h = resolution
        if os.path.exists(image_ref):
            try:
                with Image.open(image_ref) as img:
                    converted = img.convert(mode)
                    if converted.size != (target_w, target_h):
                        return converted.resize(
                            (target_w, target_h), Image.Resampling.BILINEAR
                        )
                    return converted.copy()
            except Exception as exc:
                logger.warning(
                    f"IDMVTONConditioningAdapter: Failed to load '{image_ref}': {exc}"
                )

        # Fallback dummy image if file reference is mock/absent
        if mode == "L":
            arr = np.zeros((target_h, target_w), dtype=np.uint8)
            arr[200:800, 200:568] = 255
            return Image.fromarray(arr, mode="L")

        color = (
            (240, 240, 240) if "garment" in Path(image_ref).stem else (200, 200, 200)
        )
        return Image.new("RGB", (target_w, target_h), color=color)
