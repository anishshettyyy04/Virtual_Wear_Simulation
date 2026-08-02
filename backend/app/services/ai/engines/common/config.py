from typing import Any, Dict

from pydantic import BaseModel, Field


class VTONEngineConfig(BaseModel):
    """Configuration model for Virtual Try-On (VTON) neural engines."""

    engine_name: str = Field(
        default="idm_vton", description="Identifier of target try-on engine"
    )
    model_directory: str = Field(
        default="data/models/vton/idm_vton",
        description="Path to local directory storing model checkpoints",
    )
    device: str = Field(
        default="auto", description="Target execution device (auto, cuda, cpu)"
    )
    dtype: str = Field(
        default="fp16", description="Floating-point precision (fp32, fp16, bf16)"
    )
    scheduler: str = Field(default="ddpm", description="Diffusion noise scheduler type")
    offload_mode: str = Field(
        default="sequential",
        description="CPU offload strategy (none, model, sequential)",
    )
    guidance_scale: float = Field(
        default=2.0, ge=1.0, le=20.0, description="CFG guidance scale"
    )
    num_inference_steps: int = Field(
        default=30, ge=1, le=100, description="Number of diffusion sampling steps"
    )
    enable_cpu_offload: bool = Field(
        default=True, description="Enable CPU offloading to save VRAM"
    )
    enable_vae_slicing: bool = Field(
        default=True, description="Enable VAE slicing for memory optimization"
    )
    enable_attention_slicing: bool = Field(
        default=True, description="Enable attention slicing"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary engine metadata"
    )
