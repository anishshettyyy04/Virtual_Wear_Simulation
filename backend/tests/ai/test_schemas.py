import pytest
from pydantic import ValidationError

from app.schemas.ai import ImageDimensions, PersonInput, RawTryOnOutput


def test_image_dimensions_validation() -> None:
    """Verifies ImageDimensions enforces positive integers."""
    dims = ImageDimensions(width=1920, height=1080)
    assert dims.width == 1920
    assert dims.height == 1080

    with pytest.raises(ValidationError):
        ImageDimensions(width=0, height=1080)

    with pytest.raises(ValidationError):
        ImageDimensions(width=1920, height=-5)


def test_raw_tryon_output_confidence_score_validation() -> None:
    """Verifies confidence_score range validation [0.0, 1.0] when provided."""
    valid_output = RawTryOnOutput(
        raw_render_id="r1",
        output_ref="mock://ref",
        confidence_score=0.85,
    )
    assert valid_output.confidence_score == 0.85

    none_output = RawTryOnOutput(
        raw_render_id="r2",
        output_ref="mock://ref",
        confidence_score=None,
    )
    assert none_output.confidence_score is None

    with pytest.raises(ValidationError):
        RawTryOnOutput(
            raw_render_id="r3",
            output_ref="mock://ref",
            confidence_score=1.5,
        )

    with pytest.raises(ValidationError):
        RawTryOnOutput(
            raw_render_id="r4",
            output_ref="mock://ref",
            confidence_score=-0.1,
        )


def test_mutable_defaults_isolation() -> None:
    """Verifies metadata fields do not share mutable references between instances."""
    p1 = PersonInput(person_id="p1", image_ref="ref1")
    p2 = PersonInput(person_id="p2", image_ref="ref2")

    p1.metadata["key"] = "value"
    assert "key" not in p2.metadata
