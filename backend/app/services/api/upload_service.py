import hashlib
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from fastapi import UploadFile
from PIL import Image

from app.config.settings import Settings, settings
from app.utils.logger import logger

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class UploadService:
    """Service handling streaming file uploads, image validation, and cleanup."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        self.config = config or settings
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_bytes = int(self.config.AI_INPUT_MAX_FILE_SIZE_MB * 1024 * 1024)
        self.max_width = self.config.AI_INPUT_MAX_WIDTH
        self.max_height = self.config.AI_INPUT_MAX_HEIGHT
        self.max_pixels = self.max_width * self.max_height

    async def save_uploaded_file(
        self, upload_file: UploadFile, prefix: str = "img"
    ) -> Tuple[str, int, Tuple[int, int]]:
        """Streams upload file to disk atomically, validating size and MIME."""
        filename = upload_file.filename or "upload.png"
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            allowed = list(ALLOWED_EXTENSIONS)
            raise ValueError(
                f"Unsupported file extension '{ext}'. Allowed extensions: {allowed}"
            )

        content_type = (upload_file.content_type or "").lower().strip()
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            allowed_mimes = list(ALLOWED_MIME_TYPES)
            raise ValueError(
                f"Unsupported MIME type '{content_type}'. Allowed: {allowed_mimes}"
            )

        # Stream chunks atomically
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.upload_dir, prefix=f"tmp_up_{prefix}_", suffix=ext
        )
        bytes_written = 0
        sha256 = hashlib.sha256()

        try:
            with os.fdopen(temp_fd, "wb") as f_out:
                while chunk := await upload_file.read(8192):
                    bytes_written += len(chunk)
                    if bytes_written > self.max_bytes:
                        max_mb = self.config.AI_INPUT_MAX_FILE_SIZE_MB
                        raise ValueError(
                            f"File size exceeds maximum allowed limit of {max_mb}MB."
                        )
                    sha256.update(chunk)
                    f_out.write(chunk)

            if bytes_written == 0:
                raise ValueError("Uploaded file is empty.")

            # Validate image corruption and bounds
            with Image.open(temp_path) as img:
                img.verify()

            # Re-open to read dimensions after verify()
            with Image.open(temp_path) as img:
                w, h = img.width, img.height

            if w > self.max_width or h > self.max_height:
                mw, mh = self.max_width, self.max_height
                raise ValueError(
                    f"Image dimensions ({w}x{h}) exceed max limit ({mw}x{mh})."
                )

            if (w * h) > self.max_pixels:
                raise ValueError(
                    f"Image pixel count ({w*h}) exceeds max limit of {self.max_pixels}."
                )

            hash_digest = sha256.hexdigest()[:8]
            final_filename = f"{prefix}_{hash_digest}{ext}"
            final_path = self.upload_dir / final_filename

            os.replace(temp_path, final_path)
            logger.info(
                f"UploadService: Saved '{final_filename}' ({bytes_written}b, {w}x{h})"
            )
            return str(final_path), bytes_written, (w, h)

        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    @staticmethod
    def cleanup_files(*file_paths: Optional[str]) -> None:
        """Utility removing specified file paths to prevent orphan files."""
        for path_str in file_paths:
            if path_str and os.path.exists(path_str):
                try:
                    os.remove(path_str)
                    logger.info(f"UploadService: Removed '{path_str}'")
                except Exception as exc:
                    logger.warning(
                        f"UploadService: Failed removing '{path_str}': {exc}"
                    )
