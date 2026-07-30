from pathlib import Path

import pytest
from PIL import Image

from app.config.settings import Settings
from app.schemas.ai import GarmentInput, ImageDimensions, PersonInput
from app.services.ai.exceptions import PreprocessingError
from app.services.ai.preprocessing.image_preprocessor import ImagePreprocessor


def create_test_image(
    path: Path,
    width: int,
    height: int,
    fmt: str = "JPEG",
    mode: str = "RGB",
    color: tuple = (255, 0, 0),
) -> Path:
    """Helper to create temporary test images programmatically using Pillow."""
    img = Image.new(mode, (width, height), color)
    if fmt == "JPEG" and mode == "RGBA":
        img = img.convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format=fmt)
    return path


@pytest.fixture
def custom_settings(tmp_path: Path) -> Settings:
    """Fixture providing isolated temporary settings and output directory."""
    processed_dir = tmp_path / "data" / "processed"
    return Settings(
        AI_INPUT_MAX_FILE_SIZE_MB=5.0,
        AI_INPUT_MAX_WIDTH=8192,
        AI_INPUT_MAX_HEIGHT=8192,
        AI_PREPROCESS_MAX_WIDTH=1024,
        AI_PREPROCESS_MAX_HEIGHT=1024,
        AI_PREPROCESS_OUTPUT_FORMAT="JPEG",
        AI_PREPROCESS_JPEG_QUALITY=90,
        AI_PROCESSED_DIR=str(processed_dir),
    )


@pytest.mark.asyncio
async def test_valid_jpeg_and_png_preprocessing(
    tmp_path: Path, custom_settings: Settings
) -> None:
    """Verifies preprocessing valid JPEG/PNG and re-opens outputs to decode."""
    p_path = create_test_image(tmp_path / "p.jpg", 1200, 800, fmt="JPEG")
    g_path = create_test_image(tmp_path / "g.png", 600, 600, fmt="PNG")

    preprocessor = ImagePreprocessor(config=custom_settings)
    person = PersonInput(person_id="p100", image_ref=str(p_path))
    garment = GarmentInput(garment_id="g200", image_ref=str(g_path))

    result = await preprocessor.process(person, garment)

    assert result.person_processed_id == "proc_p100"
    assert result.garment_processed_id == "proc_g200"

    # Re-open output files with Pillow to verify decoded content
    p_output = Path(result.person_image_ref)
    g_output = Path(result.garment_image_ref)

    assert p_output.exists()
    assert g_output.exists()

    with Image.open(p_output) as img:
        assert img.mode == "RGB"
        assert img.size == (1024, 682)

    with Image.open(g_output) as img:
        assert img.mode == "RGB"
        assert img.size == (600, 600)


@pytest.mark.asyncio
async def test_rgba_transparency_compositing(
    tmp_path: Path, custom_settings: Settings
) -> None:
    """Verifies transparent RGBA pixels are composited onto solid white background."""
    rgba_path = tmp_path / "transparent.png"
    img = Image.new("RGBA", (200, 200), (255, 0, 0, 128))  # 50% transparent red
    rgba_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(rgba_path, format="PNG")

    g_path = create_test_image(tmp_path / "g.jpg", 400, 400, fmt="JPEG")

    preprocessor = ImagePreprocessor(config=custom_settings)
    person = PersonInput(person_id="p_rgba", image_ref=str(rgba_path))
    garment = GarmentInput(garment_id="g_normal", image_ref=str(g_path))

    result = await preprocessor.process(person, garment)

    with Image.open(Path(result.person_image_ref)) as out_img:
        assert out_img.mode == "RGB"
        # 50% red over 100% white results in pinkish RGB (255, 127, 127)
        r, g, b = out_img.getpixel((10, 10))
        assert r == 255
        assert 120 <= g <= 135
        assert 120 <= b <= 135


@pytest.mark.asyncio
async def test_fit_within_aspect_ratio_resize(
    tmp_path: Path, custom_settings: Settings
) -> None:
    """Verifies oversized image 2000x1000 is downscaled to 1024x512."""
    p_path = create_test_image(tmp_path / "big.jpg", 2000, 1000, fmt="JPEG")
    g_path = create_test_image(tmp_path / "g.jpg", 500, 500, fmt="JPEG")

    preprocessor = ImagePreprocessor(config=custom_settings)
    person = PersonInput(person_id="p_big", image_ref=str(p_path))
    garment = GarmentInput(garment_id="g_normal", image_ref=str(g_path))

    result = await preprocessor.process(person, garment)
    assert result.person_dimensions == ImageDimensions(width=1024, height=512)


@pytest.mark.asyncio
async def test_no_unnecessary_upscaling(
    tmp_path: Path, custom_settings: Settings
) -> None:
    """Verifies small image 400x300 is not upscaled."""
    p_path = create_test_image(tmp_path / "small.jpg", 400, 300, fmt="JPEG")
    g_path = create_test_image(tmp_path / "g.jpg", 500, 500, fmt="JPEG")

    preprocessor = ImagePreprocessor(config=custom_settings)
    person = PersonInput(person_id="p_small", image_ref=str(p_path))
    garment = GarmentInput(garment_id="g_normal", image_ref=str(g_path))

    result = await preprocessor.process(person, garment)
    assert result.person_dimensions == ImageDimensions(width=400, height=300)


@pytest.mark.asyncio
async def test_oversized_input_dimensions_rejection(
    tmp_path: Path, custom_settings: Settings
) -> None:
    """Verifies oversized input dimensions raise PreprocessingError."""
    p_path = create_test_image(tmp_path / "huge.jpg", 9000, 9000, fmt="JPEG")
    g_path = create_test_image(tmp_path / "g.jpg", 500, 500, fmt="JPEG")

    preprocessor = ImagePreprocessor(config=custom_settings)
    person = PersonInput(person_id="p_huge", image_ref=str(p_path))
    garment = GarmentInput(garment_id="g_normal", image_ref=str(g_path))

    with pytest.raises(PreprocessingError, match="exceed maximum safety bounds"):
        await preprocessor.process(person, garment)


@pytest.mark.asyncio
async def test_file_size_rejection(tmp_path: Path, custom_settings: Settings) -> None:
    """Verifies file size exceeding limit raises PreprocessingError."""
    custom_settings.AI_INPUT_MAX_FILE_SIZE_MB = 0.001  # ~1 KB limit
    p_path = create_test_image(tmp_path / "large.jpg", 1000, 1000, fmt="JPEG")
    g_path = create_test_image(tmp_path / "g.jpg", 100, 100, fmt="JPEG")

    preprocessor = ImagePreprocessor(config=custom_settings)
    person = PersonInput(person_id="p_large", image_ref=str(p_path))
    garment = GarmentInput(garment_id="g_normal", image_ref=str(g_path))

    with pytest.raises(PreprocessingError, match="exceeds maximum allowed limit"):
        await preprocessor.process(person, garment)


@pytest.mark.asyncio
async def test_unsupported_format_rejection(
    tmp_path: Path, custom_settings: Settings
) -> None:
    """Verifies unsupported format (e.g. BMP) raises PreprocessingError."""
    bmp_path = create_test_image(tmp_path / "test.bmp", 100, 100, fmt="BMP")
    g_path = create_test_image(tmp_path / "g.jpg", 100, 100, fmt="JPEG")

    preprocessor = ImagePreprocessor(config=custom_settings)
    person = PersonInput(person_id="p_bmp", image_ref=str(bmp_path))
    garment = GarmentInput(garment_id="g_normal", image_ref=str(g_path))

    err_msg = "Unsupported person image format 'BMP'"
    with pytest.raises(PreprocessingError, match=err_msg):
        await preprocessor.process(person, garment)


@pytest.mark.asyncio
async def test_corrupted_and_missing_file_rejection(
    tmp_path: Path, custom_settings: Settings
) -> None:
    """Verifies missing file and corrupted pixel bytes raise PreprocessingError."""
    preprocessor = ImagePreprocessor(config=custom_settings)
    g_path = create_test_image(tmp_path / "g.jpg", 100, 100, fmt="JPEG")

    # 1. Missing file
    person_missing = PersonInput(
        person_id="p_missing", image_ref=str(tmp_path / "nonexistent.jpg")
    )
    garment = GarmentInput(garment_id="g_normal", image_ref=str(g_path))

    with pytest.raises(PreprocessingError, match="not found or unreadable"):
        await preprocessor.process(person_missing, garment)

    # 2. Corrupted file
    corrupt_path = tmp_path / "corrupt.jpg"
    corrupt_path.write_bytes(b"NOT_AN_IMAGE_FILE_HEADER_BYTES")

    person_corrupt = PersonInput(person_id="p_corrupt", image_ref=str(corrupt_path))
    with pytest.raises(PreprocessingError, match="Failed to decode or process"):
        await preprocessor.process(person_corrupt, garment)


@pytest.mark.asyncio
async def test_malicious_identifier_containment(
    tmp_path: Path, custom_settings: Settings
) -> None:
    """Verifies malicious IDs keep output inside AI_PROCESSED_DIR."""
    p_path = create_test_image(tmp_path / "p.jpg", 100, 100, fmt="JPEG")
    g_path = create_test_image(tmp_path / "g.jpg", 100, 100, fmt="JPEG")

    preprocessor = ImagePreprocessor(config=custom_settings)
    person = PersonInput(
        person_id="../../outside/malicious_user", image_ref=str(p_path)
    )
    garment = GarmentInput(
        garment_id="garment/../../../hacked", image_ref=str(g_path)
    )

    result = await preprocessor.process(person, garment)

    p_out = Path(result.person_image_ref)
    g_out = Path(result.garment_image_ref)

    processed_dir = Path(custom_settings.AI_PROCESSED_DIR).resolve()
    assert processed_dir in p_out.resolve().parents
    assert processed_dir in g_out.resolve().parents


@pytest.mark.asyncio
async def test_transaction_like_failure_cleanup(
    tmp_path: Path, custom_settings: Settings
) -> None:
    """Verifies temp files clean up when garment processing fails."""
    p_path = create_test_image(tmp_path / "p.jpg", 100, 100, fmt="JPEG")

    preprocessor = ImagePreprocessor(config=custom_settings)
    person = PersonInput(person_id="p_good", image_ref=str(p_path))
    garment_bad = GarmentInput(
        garment_id="g_bad", image_ref=str(tmp_path / "missing_garment.jpg")
    )

    with pytest.raises(PreprocessingError):
        await preprocessor.process(person, garment_bad)

    # Verify no temporary `.tmp` files left inside processed directory
    processed_dir = Path(custom_settings.AI_PROCESSED_DIR)
    if processed_dir.exists():
        temp_files = list(processed_dir.glob("**/.tmp_*"))
        assert len(temp_files) == 0
