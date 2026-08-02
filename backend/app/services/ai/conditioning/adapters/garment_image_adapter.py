import os
from typing import Any, Dict, Tuple

from PIL import Image

from app.services.ai.conditioning.base import BaseImageAdapter
from app.utils.logger import logger


class GarmentImageAdapter(BaseImageAdapter):
    """Adapter transforming canonical preprocessed garment images."""

    def adapt(
        self,
        image_ref: str,
        target_resolution: Tuple[int, int] = (768, 1024),
    ) -> Dict[str, Any]:
        """Validates and prepares garment image adaptation metadata."""
        if not image_ref:
            raise ValueError("Garment image reference cannot be empty.")

        target_w, target_h = target_resolution
        orig_w, orig_h = target_w, target_h
        has_alpha = False

        if os.path.exists(image_ref):
            try:
                with Image.open(image_ref) as img:
                    orig_w, orig_h = img.width, img.height
                    has_alpha = "A" in img.getbands()
            except Exception as exc:
                logger.warning(
                    f"GarmentImageAdapter: Failed to read image '{image_ref}': {exc}"
                )

        logger.info(
            f"GarmentImageAdapter: Prepared adaptation for '{image_ref}' "
            f"from ({orig_w}x{orig_h}) to ({target_w}x{target_h}) (alpha={has_alpha})"
        )

        return {
            "source_ref": image_ref,
            "original_resolution": (orig_w, orig_h),
            "target_resolution": (target_w, target_h),
            "has_alpha": has_alpha,
            "background_fill": "white",
            "adapter": "GarmentImageAdapter",
        }
