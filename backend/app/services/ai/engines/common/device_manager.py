from typing import Any, Dict

import torch

from app.services.ai.engines.common.exceptions import DeviceUnavailableError
from app.utils.logger import logger


class DeviceManager:
    """Utility managing hardware accelerator resolution and validation."""

    @staticmethod
    def resolve(requested_device: str = "auto") -> str:
        """Resolves target device string ('auto', 'cuda', 'cpu', 'mps')."""
        req = requested_device.lower().strip()

        if req == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
            return "cpu"

        if req in ("cuda", "cuda:0"):
            if not torch.cuda.is_available():
                raise DeviceUnavailableError(
                    requested_device=requested_device,
                    message="CUDA device requested but PyTorch CUDA is not available.",
                )
            return "cuda"

        if req == "mps":
            if not (
                hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
            ):
                raise DeviceUnavailableError(
                    requested_device=requested_device,
                    message="MPS device requested but PyTorch MPS is unavailable.",
                )
            return "mps"

        if req == "cpu":
            return "cpu"

        logger.warning(
            f"DeviceManager: Unrecognized device '{requested_device}', using CPU."
        )
        return "cpu"

    @staticmethod
    def validate(device: str) -> bool:
        """Checks if specified device is available for execution."""
        try:
            DeviceManager.resolve(device)
            return True
        except DeviceUnavailableError:
            return False

    @staticmethod
    def describe() -> Dict[str, Any]:
        """Returns diagnostic details for available execution hardware."""
        cuda_avail = torch.cuda.is_available()
        info: Dict[str, Any] = {
            "cuda_available": cuda_avail,
            "pytorch_version": torch.__version__,
            "device_count": torch.cuda.device_count() if cuda_avail else 0,
        }

        if cuda_avail:
            info["device_name"] = torch.cuda.get_device_name(0)
            mem_total_bytes = torch.cuda.get_device_properties(0).total_memory
            info["vram_total_mb"] = round(mem_total_bytes / (1024 * 1024), 2)
            info["vram_allocated_mb"] = round(
                torch.cuda.memory_allocated(0) / (1024 * 1024), 2
            )
        else:
            info["device_name"] = "CPU"

        return info
