from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class InferenceMetrics(BaseModel):
    """Standardized performance metrics model for VTON neural engine execution."""

    inference_time_ms: float = Field(
        ..., description="Diffusion sampling loop time in milliseconds"
    )
    preprocessing_time_ms: float = Field(
        default=0.0, description="Conditioning preparation time in milliseconds"
    )
    loading_time_ms: float = Field(
        default=0.0, description="Model component loading time in milliseconds"
    )
    total_time_ms: float = Field(
        ..., description="Total end-to-end execution time in milliseconds"
    )
    device: str = Field(..., description="Target execution device (cuda, cpu, mps)")
    dtype: str = Field(..., description="Tensor precision (fp32, fp16, bf16)")
    scheduler: str = Field(..., description="Diffusion noise scheduler type")
    inference_steps: int = Field(
        ..., description="Number of diffusion sampling steps executed"
    )
    guidance_scale: float = Field(..., description="CFG guidance scale value")
    peak_memory_mb: Optional[float] = Field(
        default=None, description="Peak VRAM allocation in megabytes (CUDA only)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary engine execution metadata"
    )
