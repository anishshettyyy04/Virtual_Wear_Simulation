import types
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image

from app.schemas.ai import ImageDimensions, PreprocessingResult
from app.services.ai.exceptions import HumanParsingError
from app.services.ai.parsing.labels import ProjectSemanticLabel
from app.services.ai.parsing.segformer_parser import SegFormerHumanParser


class FakeImageProcessor:
    """Fake image processor for fast deterministic testing without model downloads."""

    def __call__(self, images, return_tensors="pt"):
        import torch

        return {"pixel_values": torch.zeros((1, 3, 128, 128))}


class FakeSegFormerModel:
    """Fake SegFormer model returning deterministic logits for testing."""

    def __init__(self, target_class_id=4):
        self.target_class_id = target_class_id

    def to(self, device):
        return self

    def eval(self):
        return self

    def __call__(self, *args, **kwargs):
        import torch

        # Shape: (1, 18, 64, 64)
        logits = torch.zeros((1, 18, 64, 64))
        # Background everywhere by default (class 0)
        logits[:, 0, :, :] = 2.0
        # Face (class 11) in top area
        logits[:, 11, :20, :20] = 5.0
        # Target class (e.g. Upper-clothes class 4) in middle area
        logits[:, self.target_class_id, 20:50, 20:50] = 5.0

        return types.SimpleNamespace(logits=logits)


@pytest.fixture
def temp_person_image(tmp_path):
    """Creates a temporary valid RGB person image artifact for testing."""
    img_path = tmp_path / "proc_person_001.png"
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img.save(img_path)

    preprocessed = PreprocessingResult(
        person_processed_id="proc_person_001",
        person_image_ref=str(img_path),
        garment_processed_id="proc_garment_001",
        garment_image_ref=str(tmp_path / "proc_garment_001.png"),
        person_dimensions=ImageDimensions(width=200, height=200),
        garment_dimensions=ImageDimensions(width=200, height=200),
    )
    return preprocessed, img_path


@pytest.mark.asyncio
async def test_segformer_parser_initialization_cpu(tmp_path):
    """Verifies SegFormerHumanParser initializes with device='cpu'."""
    parser = SegFormerHumanParser(
        model_name_or_path="mock/model",
        device="cpu",
        output_dir=str(tmp_path / "parsing"),
        image_processor=FakeImageProcessor(),
        model=FakeSegFormerModel(),
    )
    assert parser.target_device == "cpu"
    assert parser.output_dir.exists()


@pytest.mark.asyncio
async def test_segformer_parser_cuda_config_behavior(tmp_path):
    """Verifies auto device fallback and explicit cuda requirement validation."""
    with patch("torch.cuda.is_available", return_value=False):
        # Auto fallback to CPU when CUDA is unavailable
        parser_auto = SegFormerHumanParser(
            model_name_or_path="mock/model",
            device="auto",
            output_dir=str(tmp_path / "parsing_auto"),
            image_processor=FakeImageProcessor(),
            model=FakeSegFormerModel(),
        )
        assert parser_auto.target_device == "cpu"

        # Explicit CUDA requirement must fail if CUDA is unavailable
        with pytest.raises(HumanParsingError) as exc_info:
            SegFormerHumanParser(
                model_name_or_path="mock/model",
                device="cuda",
                output_dir=str(tmp_path / "parsing_cuda"),
                image_processor=FakeImageProcessor(),
                model=FakeSegFormerModel(),
            )
        assert "CUDA device requested" in str(exc_info.value)


@pytest.mark.asyncio
async def test_segformer_parser_successful_parse(temp_person_image, tmp_path):
    """Verifies successful parsing, PNG mask creation, and category extraction."""
    preprocessed, _ = temp_person_image
    out_dir = tmp_path / "parsing_output"

    parser = SegFormerHumanParser(
        model_name_or_path="mattmdjaga/segformer_b2_clothes",
        device="cpu",
        output_dir=str(out_dir),
        image_processor=FakeImageProcessor(),
        model=FakeSegFormerModel(target_class_id=4),  # Upper-clothes
    )

    result = await parser.parse(preprocessed)

    assert result.mask_id.startswith("mask_proc_person_001")
    assert Path(result.mask_ref).exists()
    assert result.metadata["label_mapping_version"] == "v1"
    assert result.metadata["raw_class_count"] == 18

    # Reopen saved mask artifact and inspect pixel values & dimensions
    with Image.open(result.mask_ref) as mask_img:
        assert mask_img.mode == "L"
        assert mask_img.size == (200, 200)

        mask_arr = np.array(mask_img)
        unique_pixels = set(np.unique(mask_arr))

        # Expected mapped project labels: BACKGROUND (0), FACE (2), UPPER_GARMENT (4)
        assert int(ProjectSemanticLabel.BACKGROUND) in unique_pixels
        assert int(ProjectSemanticLabel.FACE) in unique_pixels
        assert int(ProjectSemanticLabel.UPPER_GARMENT) in unique_pixels

    assert "BACKGROUND" in result.segment_categories
    assert "FACE" in result.segment_categories
    assert "UPPER_GARMENT" in result.segment_categories


@pytest.mark.asyncio
async def test_nearest_neighbor_restoration(temp_person_image, tmp_path):
    """Verifies NEAREST neighbor interpolation prevents invalid class values."""
    preprocessed, _ = temp_person_image

    parser = SegFormerHumanParser(
        model_name_or_path="mock/model",
        device="cpu",
        output_dir=str(tmp_path / "parsing_nn"),
        image_processor=FakeImageProcessor(),
        model=FakeSegFormerModel(target_class_id=4),
    )

    result = await parser.parse(preprocessed)

    with Image.open(result.mask_ref) as mask_img:
        mask_arr = np.array(mask_img)
        unique_pixels = set(np.unique(mask_arr))

        # All pixel values must be valid ProjectSemanticLabel integer values
        valid_values = {int(label) for label in ProjectSemanticLabel}
        assert unique_pixels.issubset(valid_values)


@pytest.mark.asyncio
async def test_parser_failures(tmp_path):
    """Verifies parser failure handling for missing/corrupted files and model errors."""
    parser = SegFormerHumanParser(
        model_name_or_path="mock/model",
        device="cpu",
        output_dir=str(tmp_path / "parsing_fail"),
        image_processor=FakeImageProcessor(),
        model=FakeSegFormerModel(),
    )

    # Missing file
    missing_preprocessed = PreprocessingResult(
        person_processed_id="missing_id",
        person_image_ref=str(tmp_path / "non_existent.png"),
        garment_processed_id="garment_id",
        garment_image_ref=str(tmp_path / "garment.png"),
    )
    with pytest.raises(HumanParsingError) as exc_info:
        await parser.parse(missing_preprocessed)
    assert "does not exist" in str(exc_info.value)

    # Corrupted file
    corrupt_path = tmp_path / "corrupt.png"
    corrupt_path.write_bytes(b"not an image file")

    corrupt_preprocessed = PreprocessingResult(
        person_processed_id="corrupt_id",
        person_image_ref=str(corrupt_path),
        garment_processed_id="garment_id",
        garment_image_ref=str(tmp_path / "garment.png"),
        person_dimensions=ImageDimensions(width=100, height=100),
    )
    with pytest.raises(HumanParsingError) as exc_info:
        await parser.parse(corrupt_preprocessed)
    assert "failed" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_path_traversal_security(temp_person_image, tmp_path):
    """Verifies malicious person IDs cannot escape the output directory."""
    _, img_path = temp_person_image
    out_dir = tmp_path / "parsing_secure"

    parser = SegFormerHumanParser(
        model_name_or_path="mock/model",
        device="cpu",
        output_dir=str(out_dir),
        image_processor=FakeImageProcessor(),
        model=FakeSegFormerModel(),
    )

    malicious_preprocessed = PreprocessingResult(
        person_processed_id="../../../outside_path_traversal",
        person_image_ref=str(img_path),
        garment_processed_id="garment_001",
        garment_image_ref=str(tmp_path / "garment.png"),
    )

    result = await parser.parse(malicious_preprocessed)
    mask_file = Path(result.mask_ref)

    # Must remain strictly inside output_dir
    assert out_dir.resolve() in mask_file.resolve().parents
    assert mask_file.exists()
