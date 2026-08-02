from typing import Optional

from app.services.ai.exceptions import AIPipelineError, TryOnInferenceError


class EngineInitializationError(TryOnInferenceError):
    """Exception raised when a VTON engine fails to initialize."""

    def __init__(
        self, message: str, engine_name: str = "vton", details: Optional[str] = None
    ) -> None:
        super().__init__(
            f"Engine '{engine_name}' initialization failed: {message}",
            details=details,
        )
        self.engine_name = engine_name


class WeightMissingError(AIPipelineError):
    """Exception raised when required model weight files or checkpoints are missing."""

    def __init__(
        self,
        message: str,
        missing_assets: Optional[list[str]] = None,
        details: Optional[str] = None,
    ) -> None:
        super().__init__(message, stage="model_weight_manager", details=details)
        self.missing_assets = missing_assets or []


class InferenceError(TryOnInferenceError):
    """Exception raised during neural try-on inference execution failure."""

    def __init__(
        self, message: str, engine_name: str = "vton", details: Optional[str] = None
    ) -> None:
        super().__init__(
            f"Inference failure in engine '{engine_name}': {message}",
            details=details,
        )
        self.engine_name = engine_name


class DeviceUnavailableError(AIPipelineError):
    """Exception raised when target execution device is unavailable."""

    def __init__(
        self,
        requested_device: str,
        message: str = "Requested execution device is unavailable.",
        details: Optional[str] = None,
    ) -> None:
        super().__init__(
            f"Device '{requested_device}' unavailable: {message}",
            stage="device_manager",
            details=details,
        )
        self.requested_device = requested_device


class ConfigurationError(AIPipelineError):
    """Exception raised when VTONEngineConfig or engine parameters are invalid."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(message, stage="engine_config", details=details)
