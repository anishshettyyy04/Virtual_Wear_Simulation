import io
from pathlib import Path

import pytest
from fastapi import UploadFile
from PIL import Image

from app.services.api.upload_service import UploadService


@pytest.mark.asyncio
async def test_upload_service_save_and_cleanup(tmp_path: Path) -> None:
    """Verifies UploadService streams image upload and cleans up files."""
    service = UploadService()
    service.upload_dir = tmp_path

    # Create dummy PNG image byte stream
    img = Image.new("RGB", (200, 300), color=(255, 0, 0))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    upload_file = UploadFile(
        filename="person.png",
        file=img_byte_arr,
        headers={"content-type": "image/png"},
    )

    file_path, num_bytes, dims = await service.save_uploaded_file(
        upload_file, prefix="person"
    )
    assert Path(file_path).exists()
    assert num_bytes > 0
    assert dims == (200, 300)

    # Cleanup verification
    UploadService.cleanup_files(file_path)
    assert not Path(file_path).exists()


@pytest.mark.asyncio
async def test_upload_service_invalid_extension(tmp_path: Path) -> None:
    """Verifies UploadService rejects invalid extensions."""
    service = UploadService()
    service.upload_dir = tmp_path

    upload_file = UploadFile(
        filename="script.sh",
        file=io.BytesIO(b"echo 1"),
        headers={"content-type": "text/x-shellscript"},
    )
    with pytest.raises(ValueError) as exc_info:
        await service.save_uploaded_file(upload_file)
    assert "extension" in str(exc_info.value).lower()
