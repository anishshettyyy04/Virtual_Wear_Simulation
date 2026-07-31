from enum import IntEnum

PROJECT_SEMANTIC_LABEL_VERSION: str = "v1"


class ProjectSemanticLabel(IntEnum):
    """Model-independent stable numeric project semantic labels (v1)."""

    BACKGROUND = 0
    HAIR = 1
    FACE = 2
    HEAD_ACCESSORY = 3
    UPPER_GARMENT = 4
    LOWER_GARMENT = 5
    FULL_BODY_GARMENT = 6
    LEFT_ARM = 7
    RIGHT_ARM = 8
    LEFT_LEG = 9
    RIGHT_LEG = 10
    FOOTWEAR = 11
    OTHER = 12


SEGFORMER_B2_CLOTHES_MAPPING: dict[int, ProjectSemanticLabel] = {
    0: ProjectSemanticLabel.BACKGROUND,  # Background
    1: ProjectSemanticLabel.HEAD_ACCESSORY,  # Hat
    2: ProjectSemanticLabel.HAIR,  # Hair
    3: ProjectSemanticLabel.HEAD_ACCESSORY,  # Sunglasses
    4: ProjectSemanticLabel.UPPER_GARMENT,  # Upper-clothes
    5: ProjectSemanticLabel.LOWER_GARMENT,  # Skirt
    6: ProjectSemanticLabel.LOWER_GARMENT,  # Pants
    7: ProjectSemanticLabel.FULL_BODY_GARMENT,  # Dress
    8: ProjectSemanticLabel.OTHER,  # Belt
    9: ProjectSemanticLabel.FOOTWEAR,  # Left-shoe
    10: ProjectSemanticLabel.FOOTWEAR,  # Right-shoe
    11: ProjectSemanticLabel.FACE,  # Face
    12: ProjectSemanticLabel.LEFT_LEG,  # Left-leg
    13: ProjectSemanticLabel.RIGHT_LEG,  # Right-leg
    14: ProjectSemanticLabel.LEFT_ARM,  # Left-arm
    15: ProjectSemanticLabel.RIGHT_ARM,  # Right-arm
    16: ProjectSemanticLabel.OTHER,  # Bag
    17: ProjectSemanticLabel.HEAD_ACCESSORY,  # Scarf
}


def map_raw_class_to_project(raw_class_id: int) -> ProjectSemanticLabel:
    """Maps a raw SegFormer class ID to ProjectSemanticLabel with fallback to OTHER."""
    return SEGFORMER_B2_CLOTHES_MAPPING.get(raw_class_id, ProjectSemanticLabel.OTHER)
