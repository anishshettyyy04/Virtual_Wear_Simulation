from typing import Any

from app.services.ai.conditioning.base import BaseImageAdapter


class GarmentImageAdapter(BaseImageAdapter):
    """Adapter transforming canonical preprocessed garment images."""

    def adapt(self, image_ref: str, target_width: int, target_height: int) -> Any:
        """Transforms garment image to model target dimensions."""
        raise NotImplementedError
