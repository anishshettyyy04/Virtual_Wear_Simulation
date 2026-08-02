from typing import Any, Dict, List

from pydantic import BaseModel, Field


class EngineHealthReport(BaseModel):
    """Health check report summarizing engine readiness before initialization."""

    engine_name: str = Field(..., description="Target engine name")
    is_healthy: bool = Field(
        default=False, description="Overall engine health and readiness"
    )
    model_files_found: bool = Field(
        default=False, description="Whether all required model weight files exist"
    )
    scheduler_available: bool = Field(
        default=True, description="Whether noise scheduler configuration is valid"
    )
    vae_available: bool = Field(
        default=True, description="Whether VAE model assets are present"
    )
    unet_available: bool = Field(
        default=True, description="Whether UNet model assets are present"
    )
    config_valid: bool = Field(
        default=True, description="Whether VTONEngineConfig is valid"
    )
    execution_device_available: bool = Field(
        default=True, description="Whether configured execution device is available"
    )
    missing_files: List[str] = Field(
        default_factory=list, description="List of missing file paths"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Detailed diagnostic key-values"
    )
