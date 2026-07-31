from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # General Application Configuration
    APP_NAME: str = "Virtual Wear Simulation API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(
        default="development", pattern="^(development|staging|production|test)$"
    )
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1, le=65535)

    # Security & CORS Settings
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Storage & Upload Limits
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, gt=0)
    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )

    # AI Preprocessing Configuration (Phase 1.2.2)
    AI_INPUT_MAX_FILE_SIZE_MB: float = Field(default=20.0, gt=0.0)
    AI_INPUT_MAX_WIDTH: int = Field(default=8192, gt=0)
    AI_INPUT_MAX_HEIGHT: int = Field(default=8192, gt=0)

    AI_PREPROCESS_MAX_WIDTH: int = Field(default=1024, gt=0)
    AI_PREPROCESS_MAX_HEIGHT: int = Field(default=1024, gt=0)
    AI_PREPROCESS_OUTPUT_FORMAT: str = Field(default="JPEG")
    AI_PREPROCESS_JPEG_QUALITY: int = Field(default=95, ge=1, le=100)
    AI_PROCESSED_DIR: str = "data/processed"

    # AI Human Parser Configuration (Phase 1.2.3B)
    AI_HUMAN_PARSER_MODEL: str = "mattmdjaga/segformer_b2_clothes"
    AI_HUMAN_PARSER_DEVICE: str = Field(default="auto", pattern="^(auto|cpu|cuda)$")
    AI_HUMAN_PARSER_OUTPUT_DIR: str = "data/processed/parsing"
    AI_HUMAN_PARSER_PRECISION: str = Field(default="fp32", pattern="^(fp32|fp16)$")

    # AI Pose Estimator Configuration (Phase 1.2.4B)
    AI_POSE_MODEL_DETECTOR: str = "data/models/pose/yolox_l.onnx"
    AI_POSE_MODEL_ESTIMATOR: str = "data/models/pose/dw-ll_ucoco_384.onnx"
    AI_POSE_DEVICE: str = Field(default="auto", pattern="^(auto|cpu|cuda)$")
    AI_POSE_CONFIDENCE_THRESHOLD: float = Field(default=0.3, ge=0.0, le=1.0)
    AI_POSE_DETECTION_THRESHOLD: float = Field(default=0.4, ge=0.0, le=1.0)
    AI_POSE_OUTPUT_DIR: str = "data/processed/poses"

    # AI Agnostic Mask Generator Configuration (Phase 1.2.5B)
    AI_AGNOSTIC_MASK_OUTPUT_DIR: str = "data/processed/agnostic_masks"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[List[str], str]) -> List[str]:
        """Ensures CORS_ORIGINS is always a parsed list of origin strings."""
        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):
                import json

                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("AI_PREPROCESS_OUTPUT_FORMAT", mode="before")
    @classmethod
    def validate_output_format(cls, value: str) -> str:
        """Ensures preprocessing output format is supported."""
        formatted = value.upper().strip()
        supported = ["JPEG", "PNG", "WEBP"]
        if formatted not in supported:
            raise ValueError(
                f"Unsupported output format '{value}'. Supported formats: {supported}"
            )
        return formatted


settings = Settings()
