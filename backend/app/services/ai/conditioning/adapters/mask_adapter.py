from typing import Any

from app.services.ai.conditioning.base import BaseMaskAdapter


class IDMVTONMaskAdapter(BaseMaskAdapter):
    """Adapter transforming canonical 8-bit agnostic masks to IDM-VTON format."""

    def adapt(self, mask_ref: str, target_width: int, target_height: int) -> Any:
        """Transforms canonical agnostic mask to IDM-VTON tensor representation."""
        raise NotImplementedError
