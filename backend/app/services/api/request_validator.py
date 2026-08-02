import json
from typing import Any, Dict, Optional

from app.schemas.ai import GarmentCategory
from app.services.ai.engines import ModelRegistry


class RequestValidator:
    """Validator performing pre-pipeline request parameter checks."""

    @staticmethod
    def validate_garment_category(category: str) -> GarmentCategory:
        """Validates and parses garment category string to GarmentCategory enum."""
        if not category:
            raise ValueError("Garment category is required.")

        normalized = category.lower().strip()
        try:
            return GarmentCategory(normalized)
        except ValueError:
            valid_cats = [c.value for c in GarmentCategory]
            raise ValueError(
                f"Invalid garment category '{category}'. Valid categories: {valid_cats}"
            )

    @staticmethod
    def validate_engine(engine_name: Optional[str]) -> str:
        """Validates requested try-on engine name against registered engines."""
        target = (engine_name or "idm_vton").lower().strip()
        if not ModelRegistry.is_engine_registered(target):
            registered = ModelRegistry.get_registered_engines()
            raise ValueError(
                f"Unsupported engine '{engine_name}'. Registered: {registered}"
            )
        return target

    @staticmethod
    def parse_metadata(raw_metadata: Optional[str]) -> Dict[str, Any]:
        """Parses optional JSON metadata string."""
        if not raw_metadata:
            return {}
        try:
            parsed = json.loads(raw_metadata)
            if not isinstance(parsed, dict):
                raise ValueError("Metadata must be a valid JSON object.")
            return parsed
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON metadata string: {exc}")
