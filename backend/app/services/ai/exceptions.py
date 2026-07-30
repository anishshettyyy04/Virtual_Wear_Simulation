class AIPipelineError(Exception):
    """Base exception for all internal AI pipeline failures."""

    def __init__(
        self, message: str, stage: str = "pipeline", details: str | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.stage = stage
        self.details = details


class PreprocessingError(AIPipelineError):
    """Exception raised during input validation or preprocessing stage."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message, stage="preprocessing", details=details)


class HumanParsingError(AIPipelineError):
    """Exception raised during human segmentation parsing stage."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message, stage="human_parsing", details=details)


class PoseEstimationError(AIPipelineError):
    """Exception raised during pose estimation stage."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message, stage="pose_estimation", details=details)


class TryOnInferenceError(AIPipelineError):
    """Exception raised during virtual try-on neural engine stage."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message, stage="tryon_inference", details=details)


class PostprocessingError(AIPipelineError):
    """Exception raised during final image postprocessing stage."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message, stage="postprocessing", details=details)
