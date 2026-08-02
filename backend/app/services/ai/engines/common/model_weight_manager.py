import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.ai.engines.common.exceptions import WeightMissingError
from app.utils.logger import logger


class ModelWeightManager:
    """Manager responsible for inspecting, verifying, and locating model weights."""

    def __init__(
        self,
        model_dir: str = "data/models/vton/idm_vton",
        required_files: Optional[List[str]] = None,
        model_revision: str = "main",
        source_repository: str = "yisol/IDM-VTON",
        source_provider: str = "huggingface",
    ) -> None:
        self.model_dir = Path(model_dir)
        self.required_files = required_files or [
            "unet/diffusion_pytorch_model.safetensors",
            "unet_encoder/diffusion_pytorch_model.safetensors",
            "text_encoder_2/model.safetensors",
            "image_encoder/model.safetensors",
            "text_encoder/model.safetensors",
            "vae/diffusion_pytorch_model.safetensors",
        ]
        self.model_revision = model_revision
        self.source_repository = source_repository
        self.source_provider = source_provider
        self.checkpoint_hash: Optional[str] = None

    def locate(self) -> Path:
        """Returns resolved Path to the local model directory."""
        return self.model_dir.resolve()

    def list_missing(self) -> List[str]:
        """Inspects directory and returns list of missing required file paths."""
        missing: List[str] = []
        if not self.model_dir.exists():
            return [str(self.model_dir / file_rel) for file_rel in self.required_files]

        for file_rel in self.required_files:
            file_path = self.model_dir / file_rel
            if not file_path.exists():
                missing.append(file_rel)

        return missing

    def verify(self, raise_on_missing: bool = False) -> bool:
        """Verifies presence of all required model files."""
        missing = self.list_missing()
        if missing:
            logger.warning(
                f"ModelWeightManager: Missing {len(missing)} required weight files "
                f"in '{self.model_dir}': {missing}"
            )
            if raise_on_missing:
                raise WeightMissingError(
                    message=f"Missing required weights in '{self.model_dir}'",
                    missing_assets=missing,
                )
            return False

        logger.info(f"ModelWeightManager: Verified model weights in '{self.model_dir}'")
        return True

    def get_revision_metadata(self) -> Dict[str, Any]:
        """Exposes model revision metadata tracking information."""
        is_valid = self.verify()
        return {
            "model_revision": self.model_revision,
            "source_repository": self.source_repository,
            "source_provider": self.source_provider,
            "checkpoint_hash": self.checkpoint_hash or "uncomputed",
            "verification_status": "verified" if is_valid else "unverified",
        }

    def verify_checksums(self, expected_checksums: Dict[str, str]) -> Dict[str, bool]:
        """Verifies SHA-256 checksums for specified relative model files."""
        results: Dict[str, bool] = {}
        for rel_path, expected_hash in expected_checksums.items():
            full_path = self.model_dir / rel_path
            if not full_path.exists():
                results[rel_path] = False
                continue

            sha256 = hashlib.sha256()
            try:
                with open(full_path, "rb") as f:
                    while chunk := f.read(65536):
                        sha256.update(chunk)
                computed = sha256.hexdigest().lower()
                is_match = computed == expected_hash.lower()
                results[rel_path] = is_match
                if is_match and not self.checkpoint_hash:
                    self.checkpoint_hash = computed[:12]
            except Exception as exc:
                logger.error(
                    f"ModelWeightManager: Checksum error for '{rel_path}': {exc}"
                )
                results[rel_path] = False

        return results

    def download_stub(self, target_repo: str = "yisol/IDM-VTON") -> None:
        """Stub method for future automated model weight download hooks."""
        logger.info(
            f"ModelWeightManager.download_stub: Future hook for '{target_repo}' "
            f"targeting '{self.model_dir}'"
        )
