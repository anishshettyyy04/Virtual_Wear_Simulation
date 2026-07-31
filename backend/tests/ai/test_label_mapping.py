from app.services.ai.parsing.labels import (
    PROJECT_SEMANTIC_LABEL_VERSION,
    SEGFORMER_B2_CLOTHES_MAPPING,
    ProjectSemanticLabel,
    map_raw_class_to_project,
)


def test_project_semantic_label_explicit_integers():
    """Verifies ProjectSemanticLabel has stable explicit integer values."""
    assert int(ProjectSemanticLabel.BACKGROUND) == 0
    assert int(ProjectSemanticLabel.HAIR) == 1
    assert int(ProjectSemanticLabel.FACE) == 2
    assert int(ProjectSemanticLabel.HEAD_ACCESSORY) == 3
    assert int(ProjectSemanticLabel.UPPER_GARMENT) == 4
    assert int(ProjectSemanticLabel.LOWER_GARMENT) == 5
    assert int(ProjectSemanticLabel.FULL_BODY_GARMENT) == 6
    assert int(ProjectSemanticLabel.LEFT_ARM) == 7
    assert int(ProjectSemanticLabel.RIGHT_ARM) == 8
    assert int(ProjectSemanticLabel.LEFT_LEG) == 9
    assert int(ProjectSemanticLabel.RIGHT_LEG) == 10
    assert int(ProjectSemanticLabel.FOOTWEAR) == 11
    assert int(ProjectSemanticLabel.OTHER) == 12
    assert PROJECT_SEMANTIC_LABEL_VERSION == "v1"


def test_segformer_b2_clothes_18_classes_mapping():
    """Verifies all 18 raw SegFormer class IDs map deterministically
    to ProjectSemanticLabel.
    """

    expected_mappings = {
        0: ProjectSemanticLabel.BACKGROUND,
        1: ProjectSemanticLabel.HEAD_ACCESSORY,
        2: ProjectSemanticLabel.HAIR,
        3: ProjectSemanticLabel.HEAD_ACCESSORY,
        4: ProjectSemanticLabel.UPPER_GARMENT,
        5: ProjectSemanticLabel.LOWER_GARMENT,
        6: ProjectSemanticLabel.LOWER_GARMENT,
        7: ProjectSemanticLabel.FULL_BODY_GARMENT,
        8: ProjectSemanticLabel.OTHER,
        9: ProjectSemanticLabel.FOOTWEAR,
        10: ProjectSemanticLabel.FOOTWEAR,
        11: ProjectSemanticLabel.FACE,
        12: ProjectSemanticLabel.LEFT_LEG,
        13: ProjectSemanticLabel.RIGHT_LEG,
        14: ProjectSemanticLabel.LEFT_ARM,
        15: ProjectSemanticLabel.RIGHT_ARM,
        16: ProjectSemanticLabel.OTHER,
        17: ProjectSemanticLabel.HEAD_ACCESSORY,
    }

    assert len(SEGFORMER_B2_CLOTHES_MAPPING) == 18
    for raw_id, expected_project_label in expected_mappings.items():
        assert map_raw_class_to_project(raw_id) == expected_project_label


def test_unknown_raw_class_fallback():
    """Verifies unknown raw class IDs fall back to OTHER without crashing."""
    assert map_raw_class_to_project(18) == ProjectSemanticLabel.OTHER
    assert map_raw_class_to_project(99) == ProjectSemanticLabel.OTHER
    assert map_raw_class_to_project(-1) == ProjectSemanticLabel.OTHER
