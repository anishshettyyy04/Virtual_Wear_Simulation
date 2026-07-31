from enum import IntEnum

PROJECT_POSE_SCHEMA_VERSION: str = "v1"
PROJECT_POSE_TOPOLOGY: str = "COCO_18"


class ProjectPoseLabel(IntEnum):
    """Model-independent stable numeric project pose keypoint labels (v1)."""

    NOSE = 0
    NECK = 1  # Derived landmark
    RIGHT_SHOULDER = 2
    RIGHT_ELBOW = 3
    RIGHT_WRIST = 4
    LEFT_SHOULDER = 5
    LEFT_ELBOW = 6
    LEFT_WRIST = 7
    RIGHT_HIP = 8
    RIGHT_KNEE = 9
    RIGHT_ANKLE = 10
    LEFT_HIP = 11
    LEFT_KNEE = 12
    LEFT_ANKLE = 13
    RIGHT_EYE = 14
    LEFT_EYE = 15
    RIGHT_EAR = 16
    LEFT_EAR = 17


DWPOSE_RAW_TO_COCO18_MAPPING: dict[int, ProjectPoseLabel] = {
    0: ProjectPoseLabel.NOSE,
    1: ProjectPoseLabel.LEFT_EYE,
    2: ProjectPoseLabel.RIGHT_EYE,
    3: ProjectPoseLabel.LEFT_EAR,
    4: ProjectPoseLabel.RIGHT_EAR,
    5: ProjectPoseLabel.LEFT_SHOULDER,
    6: ProjectPoseLabel.RIGHT_SHOULDER,
    7: ProjectPoseLabel.LEFT_ELBOW,
    8: ProjectPoseLabel.RIGHT_ELBOW,
    9: ProjectPoseLabel.LEFT_WRIST,
    10: ProjectPoseLabel.RIGHT_WRIST,
    11: ProjectPoseLabel.LEFT_HIP,
    12: ProjectPoseLabel.RIGHT_HIP,
    13: ProjectPoseLabel.LEFT_KNEE,
    14: ProjectPoseLabel.RIGHT_KNEE,
    15: ProjectPoseLabel.LEFT_ANKLE,
    16: ProjectPoseLabel.RIGHT_ANKLE,
}
