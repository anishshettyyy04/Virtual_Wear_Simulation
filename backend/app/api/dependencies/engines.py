from typing import Optional

from app.services.ai.engines import ModelRegistry
from app.services.ai.engines.idm_vton import IDMVTONEngine
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.services.ai.mock.tryon_engine import MockTryOnEngine
from app.utils.logger import logger

_engine_instances = {}


def get_tryon_engine(engine_name: Optional[str] = None) -> BaseTryOnEngine:
    """Dependency provider resolving requested try-on engine instance."""
    name = (engine_name or "idm_vton").lower().strip()

    if name in _engine_instances:
        return _engine_instances[name]

    if name == "mock_vton":
        instance = MockTryOnEngine()
        _engine_instances[name] = instance
        return instance

    if ModelRegistry.is_engine_registered(name):
        logger.info(f"get_tryon_engine: Resolving engine instance for '{name}'")
        instance = IDMVTONEngine()
        _engine_instances[name] = instance
        return instance

    logger.warning(
        f"get_tryon_engine: Engine '{name}' not found. Falling back to IDMVTONEngine."
    )
    instance = IDMVTONEngine()
    _engine_instances[name] = instance
    return instance
