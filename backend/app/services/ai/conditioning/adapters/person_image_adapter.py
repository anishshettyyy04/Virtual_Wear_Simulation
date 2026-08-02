import os
from typing import Any, Dict, Tuple

from PIL import Image

from app.services.ai.conditioning.base import BaseImageAdapter
from app.utils.logger import logger


class PersonImageAdapter(BaseImageAdapter):
    """Adapter transforming canonical preprocessed person images."""

    def adapt(
        self,
        image_ref: str,
        target_resolution: Tuple[int, int] = (768, 1024),
    ) -> Dict[str, Any]:
        """Validates and prepares person image adaptation metadata."""
        if not image_ref:
            raise ValueError("Person image reference cannot be empty.")

        target_w, target_h = target_resolution
        orig_w, orig_h = target_w, target_h

        if os.path.exists(image_ref):
            try:
                with Image.open(image_ref) as img:
                    orig_w, orig_h = img.width, img.height
            except Exception as exc:
                logger.warning(
                    f"PersonImageAdapter: Failed to read image '{image_ref}': {exc}"
                )

        logger.info(
            f"PersonImageAdapter: Prepared adaptation for '{image_ref}' "
            f"from ({orig_w}x{orig_h}) to ({target_w}x{target_h})"
        )

        return {
            "source_ref": image_ref,
            "original_resolution": (orig_w, orig_h),
            "target_resolution": (target_w, target_h),
            "adapter": "PersonImageAdapter",
            "crop_policy": "center_crop_3_4",
        }
