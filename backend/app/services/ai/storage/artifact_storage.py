import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from PIL import Image

from app.utils.logger import logger


class ArtifactStorage:
    """Centralized storage manager for atomic file writes and artifact naming."""

    def __init__(self, base_output_dir: str = "data/processed") -> None:
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    def generate_artifact_id(
        self, prefix: str, source_ref: str, extra_seed: str = ""
    ) -> Tuple[str, str]:
        """Generates collision-resistant artifact ID and safe filename."""
        safe_stem = Path(source_ref).stem.replace(" ", "_")
        digest_input = f"{source_ref}_{extra_seed}".encode("utf-8")
        short_hash = hashlib.sha256(digest_input).hexdigest()[:8]
        artifact_id = f"{prefix}_{safe_stem}_{short_hash}"
        return artifact_id, f"{artifact_id}.png"

    def save_image_atomically(
        self,
        image: Union[Image.Image, Any],
        output_dir: Union[str, Path],
        filename: str,
        format: str = "PNG",
        quality: int = 95,
    ) -> str:
        """Atomically saves PIL Image to directory using temp file replacement."""
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        final_path = out_dir / filename

        temp_fd, temp_path = tempfile.mkstemp(
            dir=out_dir, prefix="tmp_art_", suffix=f".{format.lower()}"
        )
        os.close(temp_fd)

        try:
            if isinstance(image, Image.Image):
                save_kwargs: Dict[str, Any] = {"format": format}
                if format.upper() in ("JPEG", "JPG", "WEBP"):
                    save_kwargs["quality"] = quality
                image.save(temp_path, **save_kwargs)
            else:
                raise TypeError(
                    f"Unsupported image type '{type(image)}'. Expected PIL.Image."
                )

            os.replace(temp_path, final_path)
            logger.info(f"ArtifactStorage: Saved artifact atomically to '{final_path}'")
            return str(final_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def create_metadata(
        self,
        artifact_id: str,
        file_path: str,
        artifact_type: str,
        dimensions: Optional[Tuple[int, int]] = None,
        generator_version: str = "1.0.0",
        additional_meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generates standardized artifact metadata structure."""
        meta: Dict[str, Any] = {
            "artifact_id": artifact_id,
            "artifact_path": file_path,
            "artifact_type": artifact_type,
            "generator_version": generator_version,
            "storage_provider": "local_filesystem",
        }
        if dimensions:
            meta["width"], meta["height"] = dimensions
        if additional_meta:
            meta.update(additional_meta)
        return meta
