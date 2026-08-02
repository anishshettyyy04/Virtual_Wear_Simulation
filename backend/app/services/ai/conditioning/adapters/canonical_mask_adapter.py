import os
from typing import Any, Dict, Tuple

import numpy as np
from PIL import Image

from app.services.ai.conditioning.base import BaseMaskAdapter
from app.utils.logger import logger


class CanonicalMaskAdapter(BaseMaskAdapter):
    """Adapter validating and preparing canonical 8-bit agnostic masks."""

    def adapt(
        self,
        mask_ref: str,
        target_resolution: Tuple[int, int] = (768, 1024),
    ) -> Dict[str, Any]:
        """Validates canonical mask and prepares adaptation metadata."""
        if not mask_ref:
            raise ValueError("Mask reference cannot be empty.")

        target_w, target_h = target_resolution
        orig_w, orig_h = target_w, target_h
        coverage = 0.0

        if os.path.exists(mask_ref):
            try:
                with Image.open(mask_ref) as img:
                    orig_w, orig_h = img.width, img.height
                    mask_arr = np.array(img.convert("L"))
                    total_pixels = mask_arr.size
                    if total_pixels > 0:
                        coverage = float(np.count_nonzero(mask_arr >= 128)) / float(
                            total_pixels
                        )
            except Exception as exc:
                logger.warning(
                    f"CanonicalMaskAdapter: Failed to inspect mask '{mask_ref}': {exc}"
                )

        logger.info(
            f"CanonicalMaskAdapter: Prepared mask for '{mask_ref}' "
            f"from ({orig_w}x{orig_h}) to ({target_w}x{target_h}) "
            f"(coverage={coverage:.2f})"
        )

        return {
            "source_ref": mask_ref,
            "original_resolution": (orig_w, orig_h),
            "target_resolution": (target_w, target_h),
            "replace_coverage": round(coverage, 4),
            "adapter": "CanonicalMaskAdapter",
            "polarity": "0=preserve, 255=inpaint_hole",
        }


# Alias for backward compatibility
IDMVTONMaskAdapter = CanonicalMaskAdapter
