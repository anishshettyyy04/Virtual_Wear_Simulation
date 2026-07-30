import hashlib
import os
import re
from pathlib import Path
from typing import Any, Dict, Tuple

from PIL import Image, ImageOps

from app.config.settings import settings
from app.schemas.ai import (
    GarmentInput,
    ImageDimensions,
    PersonInput,
    PreprocessingResult,
)
from app.services.ai.exceptions import PreprocessingError
from app.services.ai.interfaces.preprocessor import BasePreprocessor
from app.utils.logger import logger

FORMAT_EXTENSION_MAP = {
    "JPEG": ".jpg",
    "JPG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}


class ImagePreprocessor(BasePreprocessor):
    """Production-grade image preprocessing service using Pillow."""

    def __init__(self, config: Any = settings) -> None:
        self.max_file_size_mb = config.AI_INPUT_MAX_FILE_SIZE_MB
        self.max_input_w = config.AI_INPUT_MAX_WIDTH
        self.max_input_h = config.AI_INPUT_MAX_HEIGHT

        self.max_target_w = config.AI_PREPROCESS_MAX_WIDTH
        self.max_target_h = config.AI_PREPROCESS_MAX_HEIGHT
        self.output_format = config.AI_PREPROCESS_OUTPUT_FORMAT.upper()
        self.jpeg_quality = config.AI_PREPROCESS_JPEG_QUALITY
        self.processed_dir = Path(config.AI_PROCESSED_DIR)

        if self.output_format not in FORMAT_EXTENSION_MAP:
            raise PreprocessingError(
                f"Unsupported configured output format '{self.output_format}'"
            )
        self.output_ext = FORMAT_EXTENSION_MAP[self.output_format]

    def _sanitize_identifier(self, raw_id: str) -> str:
        """Derives collision-resistant identifier combining name and SHA-256 hash."""
        clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_id).strip("_")
        if not clean_name:
            clean_name = "resource"
        digest_prefix = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:8]
        return f"{clean_name}_{digest_prefix}"

    def _preprocess_single_image(
        self, input_ref: str, resource_type: str, raw_id: str
    ) -> Tuple[Path, Path, str, ImageDimensions, ImageDimensions, Dict[str, Any]]:
        """Validates, decodes, transposes EXIF, normalizes RGB, and resizes image."""
        src_path = Path(input_ref)

        if not src_path.exists() or not src_path.is_file():
            raise PreprocessingError(
                f"{resource_type.capitalize()} image resource not found "
                f"or unreadable: '{input_ref}'"
            )

        file_size_mb = src_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise PreprocessingError(
                f"{resource_type.capitalize()} image file size ({file_size_mb:.2f} MB) "
                f"exceeds maximum allowed limit ({self.max_file_size_mb} MB)"
            )

        try:
            with Image.open(src_path) as img:
                # Force full pixel decoding to catch truncated/corrupted images
                img.load()
                orig_format = img.format.upper() if img.format else "UNKNOWN"

                allowed_formats = ["JPEG", "JPG", "PNG", "WEBP"]
                if orig_format not in allowed_formats:
                    raise PreprocessingError(
                        f"Unsupported {resource_type} image format '{orig_format}'. "
                        f"Supported formats: {allowed_formats}"
                    )

                # EXIF Orientation Transpose
                transposed_img = ImageOps.exif_transpose(img)
                orig_w, orig_h = transposed_img.size

                if orig_w > self.max_input_w or orig_h > self.max_input_h:
                    raise PreprocessingError(
                        f"{resource_type.capitalize()} dimensions ({orig_w}x{orig_h}) "
                        f"exceed maximum safety bounds "
                        f"({self.max_input_w}x{self.max_input_h})"
                    )

                orig_mode = transposed_img.mode

                # Color & Transparency Normalization to RGB
                if transposed_img.mode in ("RGBA", "LA") or (
                    transposed_img.mode == "P" and "transparency" in transposed_img.info
                ):
                    rgba_img = transposed_img.convert("RGBA")
                    background = Image.new("RGB", rgba_img.size, (255, 255, 255))
                    background.paste(rgba_img, mask=rgba_img.split()[3])
                    processed_img = background
                else:
                    processed_img = transposed_img.convert("RGB")

                # FIT_WITHIN Proportional Aspect-Ratio Resizing
                ratio = min(
                    self.max_target_w / float(orig_w),
                    self.max_target_h / float(orig_h),
                )

                if ratio < 1.0:
                    new_w = max(1, int(orig_w * ratio))
                    new_h = max(1, int(orig_h * ratio))
                    processed_img = processed_img.resize(
                        (new_w, new_h), Image.Resampling.LANCZOS
                    )
                    resized = True
                else:
                    new_w, new_h = orig_w, orig_h
                    resized = False

                safe_id = self._sanitize_identifier(raw_id)
                output_filename = f"proc_{resource_type}_{safe_id}{self.output_ext}"

                dest_dir = self.processed_dir / resource_type
                dest_dir.mkdir(parents=True, exist_ok=True)

                temp_path = dest_dir / f".tmp_{output_filename}"
                final_path = dest_dir / output_filename

                # Portable project-relative reference path with forward slashes
                rel_ref_path = (
                    f"{self.processed_dir.as_posix()}/{resource_type}/{output_filename}"
                )

                save_kwargs: Dict[str, Any] = {"format": self.output_format}
                if self.output_format == "JPEG":
                    save_kwargs["quality"] = self.jpeg_quality

                processed_img.save(temp_path, **save_kwargs)

                metadata: Dict[str, Any] = {
                    "original_format": orig_format,
                    "original_mode": orig_mode,
                    "color_mode": "RGB",
                    "resized": resized,
                    "output_format": self.output_format,
                }

                return (
                    temp_path,
                    final_path,
                    rel_ref_path,
                    ImageDimensions(width=orig_w, height=orig_h),
                    ImageDimensions(width=new_w, height=new_h),
                    metadata,
                )

        except PreprocessingError:
            raise
        except Image.DecompressionBombError as exc:
            raise PreprocessingError(
                f"Decompression bomb detected in {resource_type} image: {exc}"
            ) from exc
        except Exception as exc:
            raise PreprocessingError(
                f"Failed to decode or process {resource_type} image: {exc}"
            ) from exc

    async def process(
        self, person: PersonInput, garment: GarmentInput
    ) -> PreprocessingResult:
        """Validates and processes person and garment image resources atomically."""
        logger.info(
            f"ImagePreprocessor: Starting real image preprocessing for person "
            f"'{person.person_id}' and garment '{garment.garment_id}'"
        )

        p_temp = p_final = g_temp = g_final = None

        try:
            # 1. Process Person Image
            (
                p_temp,
                p_final,
                p_ref,
                p_orig_dims,
                p_proc_dims,
                p_meta,
            ) = self._preprocess_single_image(
                person.image_ref, "person", person.person_id
            )

            # 2. Process Garment Image
            (
                g_temp,
                g_final,
                g_ref,
                g_orig_dims,
                g_proc_dims,
                g_meta,
            ) = self._preprocess_single_image(
                garment.image_ref, "garment", garment.garment_id
            )

            # 3. Transaction-Like Two-Artifact Atomic Commit
            os.replace(p_temp, p_final)
            p_temp = None  # Successfully committed

            os.replace(g_temp, g_final)
            g_temp = None  # Successfully committed

            logger.info("ImagePreprocessor: Successfully committed artifacts")

            return PreprocessingResult(
                person_processed_id=f"proc_{person.person_id}",
                person_image_ref=p_ref,
                garment_processed_id=f"proc_{garment.garment_id}",
                garment_image_ref=g_ref,
                person_dimensions=p_proc_dims,
                garment_dimensions=g_proc_dims,
                normalized_metadata={
                    "person": p_meta,
                    "garment": g_meta,
                },
            )

        except Exception as exc:
            # Cleanup any uncommitted temporary files
            for temp_file in (p_temp, g_temp):
                if temp_file and temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass

            if isinstance(exc, PreprocessingError):
                raise
            raise PreprocessingError(
                f"Image preprocessing operation failed: {exc}"
            ) from exc
