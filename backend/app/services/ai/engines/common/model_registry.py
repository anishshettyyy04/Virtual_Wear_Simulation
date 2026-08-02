from typing import Any, Dict, List, Optional

from app.utils.logger import logger


class ModelRegistry:
    """Centralized metadata registry for virtual try-on neural engines."""

    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_engine(
        cls,
        engine_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registers a try-on engine name and associated metadata."""
        name = engine_name.lower().strip()
        meta = metadata or {}
        cls._registry[name] = {
            "engine_name": name,
            "registered_version": meta.get("version", "1.0.0"),
            "license": meta.get("license", "unknown"),
            "metadata": meta,
        }
        logger.info(f"ModelRegistry: Registered engine '{name}'")

    @classmethod
    def is_engine_registered(cls, engine_name: str) -> bool:
        """Checks if specified engine is registered."""
        return engine_name.lower().strip() in cls._registry

    @classmethod
    def get_engine_info(cls, engine_name: str) -> Dict[str, Any]:
        """Retrieves metadata dict for a registered engine."""
        name = engine_name.lower().strip()
        if name not in cls._registry:
            raise KeyError(
                f"Engine '{engine_name}' is not registered in ModelRegistry."
            )
        return cls._registry[name]

    @classmethod
    def get_registered_engines(cls) -> List[str]:
        """Returns list of all registered engine names."""
        return list(cls._registry.keys())

    @classmethod
    def reset(cls) -> None:
        """Resets registry mapping (primarily for testing)."""
        cls._registry.clear()


# Pre-register standard engine identifiers
ModelRegistry.register_engine(
    "idm_vton",
    metadata={
        "version": "1.0.0",
        "description": "IDM-VTON Dual-UNet SDXL Inpainting Engine",
        "license": "CC BY-NC-SA 4.0",
    },
)
ModelRegistry.register_engine(
    "catvton",
    metadata={
        "version": "1.0.0",
        "description": "CatVTON Lightweight Try-on Engine",
        "license": "Apache 2.0",
    },
)
ModelRegistry.register_engine(
    "stableviton",
    metadata={
        "version": "1.0.0",
        "description": "StableVITON Structural Warp Engine",
        "license": "Research",
    },
)
