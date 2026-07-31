from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ImageDimensions(BaseModel):
    """Represents image pixel dimensions with positive integer validation."""

    width: int = Field(..., gt=0, json_schema_extra={"example": 1024})
    height: int = Field(..., gt=0, json_schema_extra={"example": 1024})


class PersonInput(BaseModel):
    """Internal contract for person / avatar input image resource."""

    person_id: str = Field(..., json_schema_extra={"example": "person_001"})
    image_ref: str = Field(
        ..., json_schema_extra={"example": "storage://avatars/person_001.jpg"}
    )
    dimensions: Optional[ImageDimensions] = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GarmentInput(BaseModel):
    """Internal contract for apparel garment input image resource."""

    garment_id: str = Field(..., json_schema_extra={"example": "garment_001"})
    image_ref: str = Field(
        ..., json_schema_extra={"example": "storage://garments/shirt_001.jpg"}
    )
    category: str = Field(
        default="upper_body", json_schema_extra={"example": "upper_body"}
    )
    dimensions: Optional[ImageDimensions] = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PreprocessingResult(BaseModel):
    """Contract emitted by preprocessing stage containing normalized resources."""

    person_processed_id: str = Field(
        ..., json_schema_extra={"example": "proc_person_001"}
    )
    person_image_ref: str = Field(
        ..., json_schema_extra={"example": "storage://preprocessed/person_001.png"}
    )

    garment_processed_id: str = Field(
        ..., json_schema_extra={"example": "proc_garment_001"}
    )
    garment_image_ref: str = Field(
        ..., json_schema_extra={"example": "storage://preprocessed/garment_001.png"}
    )

    person_dimensions: Optional[ImageDimensions] = Field(default=None)
    garment_dimensions: Optional[ImageDimensions] = Field(default=None)

    normalized_metadata: dict[str, Any] = Field(default_factory=dict)


class HumanParsingResult(BaseModel):
    """Contract emitted by human parsing stage containing segmentation metadata."""

    mask_id: str = Field(..., json_schema_extra={"example": "mask_001"})
    mask_ref: Optional[str] = Field(
        default=None, json_schema_extra={"example": "storage://masks/mask_001.png"}
    )
    segment_categories: List[str] = Field(
        default_factory=list,
        json_schema_extra={
            "example": ["head", "upper_body", "lower_body", "background"]
        },
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class PoseEstimationResult(BaseModel):
    """Contract emitted by pose estimation stage containing skeletal keypoint info."""

    pose_id: str = Field(..., json_schema_extra={"example": "pose_001"})
    pose_ref: Optional[str] = Field(
        default=None, json_schema_extra={"example": "storage://poses/pose_001.json"}
    )
    keypoints_summary: Optional[str] = Field(
        default=None, json_schema_extra={"example": "33 keypoints aligned"}
    )
    num_keypoints: int = Field(default=33, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RawTryOnOutput(BaseModel):
    """Contract emitted by VTON engine stage prior to postprocessing."""

    raw_render_id: str = Field(..., json_schema_extra={"example": "raw_vton_001"})
    output_ref: str = Field(
        ..., json_schema_extra={"example": "storage://raw_renders/vton_001.png"}
    )
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    model_name: str = Field(default="mock", json_schema_extra={"example": "mock"})
    model_version: Optional[str] = Field(
        default="1.0.0", json_schema_extra={"example": "1.0.0"}
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class PostprocessingResult(BaseModel):
    """Contract emitted by final postprocessing stage."""

    final_image_id: str = Field(..., json_schema_extra={"example": "final_tryon_001"})
    output_ref: str = Field(
        ..., json_schema_extra={"example": "storage://results/tryon_001.jpg"}
    )
    dimensions: Optional[ImageDimensions] = Field(default=None)
    format: str = Field(default="jpeg", json_schema_extra={"example": "jpeg"})
    metadata: dict[str, Any] = Field(default_factory=dict)


class TryOnResult(BaseModel):
    """Aggregated final pipeline result contract returned to orchestrator caller."""

    final: PostprocessingResult
    pipeline_metadata: dict[str, Any] = Field(default_factory=dict)
