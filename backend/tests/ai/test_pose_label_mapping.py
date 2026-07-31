import numpy as np
import pytest

from app.services.ai.pose.adapter import map_dwpose_to_project_coco18
from app.services.ai.pose.labels import (
    DWPOSE_RAW_TO_COCO18_MAPPING,
    PROJECT_POSE_SCHEMA_VERSION,
    PROJECT_POSE_TOPOLOGY,
    ProjectPoseLabel,
)


def test_project_pose_label_explicit_ids():
    """Verify explicit stable numeric integer IDs (v1)."""
    assert PROJECT_POSE_SCHEMA_VERSION == "v1"
    assert PROJECT_POSE_TOPOLOGY == "COCO_18"
    assert ProjectPoseLabel.NOSE == 0
    assert ProjectPoseLabel.NECK == 1
    assert ProjectPoseLabel.RIGHT_SHOULDER == 2
    assert ProjectPoseLabel.RIGHT_ELBOW == 3
    assert ProjectPoseLabel.RIGHT_WRIST == 4
    assert ProjectPoseLabel.LEFT_SHOULDER == 5
    assert ProjectPoseLabel.LEFT_ELBOW == 6
    assert ProjectPoseLabel.LEFT_WRIST == 7
    assert ProjectPoseLabel.RIGHT_HIP == 8
    assert ProjectPoseLabel.RIGHT_KNEE == 9
    assert ProjectPoseLabel.RIGHT_ANKLE == 10
    assert ProjectPoseLabel.LEFT_HIP == 11
    assert ProjectPoseLabel.LEFT_KNEE == 12
    assert ProjectPoseLabel.LEFT_ANKLE == 13
    assert ProjectPoseLabel.RIGHT_EYE == 14
    assert ProjectPoseLabel.LEFT_EYE == 15
    assert ProjectPoseLabel.RIGHT_EAR == 16
    assert ProjectPoseLabel.LEFT_EAR == 17


def test_dwpose_reindexing_mapping_correctness():
    """Verify re-indexing from raw DWPose/COCO-17 indices to Project COCO-18."""
    assert DWPOSE_RAW_TO_COCO18_MAPPING[0] == ProjectPoseLabel.NOSE
    assert DWPOSE_RAW_TO_COCO18_MAPPING[1] == ProjectPoseLabel.LEFT_EYE
    assert DWPOSE_RAW_TO_COCO18_MAPPING[2] == ProjectPoseLabel.RIGHT_EYE
    assert DWPOSE_RAW_TO_COCO18_MAPPING[3] == ProjectPoseLabel.LEFT_EAR
    assert DWPOSE_RAW_TO_COCO18_MAPPING[4] == ProjectPoseLabel.RIGHT_EAR
    assert DWPOSE_RAW_TO_COCO18_MAPPING[5] == ProjectPoseLabel.LEFT_SHOULDER
    assert DWPOSE_RAW_TO_COCO18_MAPPING[6] == ProjectPoseLabel.RIGHT_SHOULDER
    assert DWPOSE_RAW_TO_COCO18_MAPPING[7] == ProjectPoseLabel.LEFT_ELBOW
    assert DWPOSE_RAW_TO_COCO18_MAPPING[8] == ProjectPoseLabel.RIGHT_ELBOW
    assert DWPOSE_RAW_TO_COCO18_MAPPING[9] == ProjectPoseLabel.LEFT_WRIST
    assert DWPOSE_RAW_TO_COCO18_MAPPING[10] == ProjectPoseLabel.RIGHT_WRIST
    assert DWPOSE_RAW_TO_COCO18_MAPPING[11] == ProjectPoseLabel.LEFT_HIP
    assert DWPOSE_RAW_TO_COCO18_MAPPING[12] == ProjectPoseLabel.RIGHT_HIP
    assert DWPOSE_RAW_TO_COCO18_MAPPING[13] == ProjectPoseLabel.LEFT_KNEE
    assert DWPOSE_RAW_TO_COCO18_MAPPING[14] == ProjectPoseLabel.RIGHT_KNEE
    assert DWPOSE_RAW_TO_COCO18_MAPPING[15] == ProjectPoseLabel.LEFT_ANKLE
    assert DWPOSE_RAW_TO_COCO18_MAPPING[16] == ProjectPoseLabel.RIGHT_ANKLE


def test_derived_neck_generation():
    """Verify derived NECK calculation when both shoulders are valid."""
    # Create raw 17 keypoints with Left Shoulder (idx 5) and Right Shoulder (idx 6)
    raw_kpts = np.zeros((17, 3), dtype=np.float32)
    # L_SHOULDER (5): x=0.6, y=0.3, conf=0.9
    raw_kpts[5] = [0.6, 0.3, 0.9]
    # R_SHOULDER (6): x=0.4, y=0.3, conf=0.8
    raw_kpts[6] = [0.4, 0.3, 0.8]

    keypoints, valid_count = map_dwpose_to_project_coco18(
        raw_kpts, image_width=1000, image_height=1000, confidence_threshold=0.3
    )

    # Check NECK slot (index 1)
    neck = keypoints[1]
    assert neck["name"] == "NECK"
    assert neck["derived"] is True
    assert neck["visible"] is True
    assert pytest.approx(neck["x"], abs=1e-3) == 0.5
    assert pytest.approx(neck["y"], abs=1e-3) == 0.3
    assert neck["x_px"] == 500
    assert neck["y_px"] == 300
    assert pytest.approx(neck["confidence"], abs=1e-3) == 0.8
    assert valid_count == 3  # L_Shoulder, R_Shoulder, Neck


def test_derived_neck_missing_behavior():
    """Verify derived NECK is missing if either shoulder confidence is low."""
    raw_kpts = np.zeros((17, 3), dtype=np.float32)
    # L_SHOULDER (5): high conf
    raw_kpts[5] = [0.6, 0.3, 0.9]
    # R_SHOULDER (6): low conf below threshold 0.3
    raw_kpts[6] = [0.4, 0.3, 0.1]

    keypoints, valid_count = map_dwpose_to_project_coco18(
        raw_kpts, image_width=1000, image_height=1000, confidence_threshold=0.3
    )

    neck = keypoints[1]
    assert neck["name"] == "NECK"
    assert neck["derived"] is True
    assert neck["visible"] is False
    assert neck["x"] is None
    assert neck["y"] is None
    assert neck["x_px"] is None
    assert neck["y_px"] is None

    assert neck["confidence"] == 0.0
    assert valid_count == 1  # Only L_Shoulder


def test_missing_keypoint_null_coordinates_representation():
    """Verify missing keypoints use explicit null coordinates."""
    raw_kpts = np.zeros((17, 3), dtype=np.float32)  # All zero confidence

    keypoints, valid_count = map_dwpose_to_project_coco18(
        raw_kpts, image_width=500, image_height=500, confidence_threshold=0.3
    )

    assert len(keypoints) == 18
    assert valid_count == 0

    for kpt in keypoints:
        assert kpt["visible"] is False
        assert kpt["x"] is None
        assert kpt["y"] is None
        assert kpt["x_px"] is None
        assert kpt["y_px"] is None
        assert kpt["confidence"] == 0.0
