from typing import Any

from app.services.ai.conditioning.base import BaseImageAdapter


class PersonImageAdapter(BaseImageAdapter):
    """Adapter transforming canonical preprocessed person images."""

    def adapt(self, image_ref: str, target_width: int, target_height: int) -> Any:
        """Transforms person image to model target dimensions."""
        raise NotImplementedError
