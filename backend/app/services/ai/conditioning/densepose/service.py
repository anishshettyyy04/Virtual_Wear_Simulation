import hashlib
import os
import tempfile
from pathlib import Path
from typing import Optional

from PIL import Image

from app.config.settings import Settings, settings
from app.schemas.ai import DensePoseResult
from app.services.ai.conditioning.base import BaseDensePoseService
from app.utils.logger import logger


class DensePoseService(BaseDensePoseService):
    """Deterministic placeholder service for DensePose body surface map generation."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        self.config = config or settings
        self.output_dir = Path(self.config.AI_DENSEPOSE_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def process(self, person_image_ref: str) -> DensePoseResult:
        """Generates a deterministic DensePose IUV surface map artifact."""
        safe_id = Path(person_image_ref).stem.replace(" ", "_")
        hash_digest = hashlib.sha256(person_image_ref.encode("utf-8")).hexdigest()[:8]
        dp_id = f"dp_{safe_id}_{hash_digest}"
        output_path = self.output_dir / f"{dp_id}.png"

        target_w = self.config.AI_IMAGE_TARGET_WIDTH
        target_h = self.config.AI_IMAGE_TARGET_HEIGHT

        # Read dimensions from source image if available
        if os.path.exists(person_image_ref):
            try:
                with Image.open(person_image_ref) as img:
                    target_w, target_h = img.width, img.height
            except Exception as exc:
                logger.warning(f"DensePoseService: Failed reading dimensions: {exc}")

        # Generate deterministic placeholder 3-channel RGB surface map visualization
        if not output_path.exists():
            img_dp = Image.new("RGB", (target_w, target_h), color=(30, 144, 255))
            temp_fd, temp_path = tempfile.mkstemp(
                dir=self.output_dir, prefix="tmp_dp_", suffix=".png"
            )
            os.close(temp_fd)
            try:
                img_dp.save(temp_path, format="PNG")
                os.replace(temp_path, output_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        logger.info(
            f"DensePoseService: Surface map generated at '{output_path}' "
            f"({target_w}x{target_h})"
        )

        return DensePoseResult(
            densepose_id=dp_id,
            densepose_ref=str(output_path),
            width=target_w,
            height=target_h,
            metadata={
                "implementation": "placeholder",
                "provider": "mock_densepose",
                "schema_version": "v1",
            },
        )


# Alias for mock service
MockDensePoseService = DensePoseService
