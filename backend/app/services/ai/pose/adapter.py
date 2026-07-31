from typing import Any, Dict, List, Tuple

from app.services.ai.pose.labels import (
    DWPOSE_RAW_TO_COCO18_MAPPING,
    ProjectPoseLabel,
)


def map_dwpose_to_project_coco18(
    raw_keypoints: Any,
    image_width: int,
    image_height: int,
    confidence_threshold: float = 0.3,
) -> Tuple[List[Dict[str, Any]], int]:
    """Maps raw DWPose/COCO-17 keypoints array to Project COCO-18 schema.

    Args:
        raw_keypoints: Keypoints array of shape (N, 3) where N >= 17,
            with rows [x, y, conf].
        image_width: Width of preprocessed image in pixels.
        image_height: Height of preprocessed image in pixels.
        confidence_threshold: Minimum confidence score to mark keypoint visible.

    Returns:
        Tuple containing list of 18 keypoint dictionaries and count of valid keypoints.
    """
    if image_width <= 0 or image_height <= 0:
        raise ValueError(f"Invalid image dimensions: {image_width}x{image_height}")

    # Initialize empty 18 slots
    slots: Dict[int, Dict[str, Any]] = {}
    for label in ProjectPoseLabel:
        slots[int(label)] = {
            "id": int(label),
            "name": label.name,
            "x": None,
            "y": None,
            "x_px": None,
            "y_px": None,
            "confidence": 0.0,
            "visible": False,
            "derived": False,
        }

    # Map directly predicted DWPose keypoints
    for raw_idx, project_label in DWPOSE_RAW_TO_COCO18_MAPPING.items():
        slot_id = int(project_label)
        if raw_idx < len(raw_keypoints):
            kpt = raw_keypoints[raw_idx]
            x_raw, y_raw = float(kpt[0]), float(kpt[1])
            conf = float(kpt[2])

            if conf >= confidence_threshold:
                # Check if coordinates are normalized [0, 1] or pixel space
                if 0.0 <= x_raw <= 1.0 and 0.0 <= y_raw <= 1.0:
                    norm_x = max(0.0, min(1.0, x_raw))
                    norm_y = max(0.0, min(1.0, y_raw))
                    px_x = int(round(norm_x * image_width))
                    px_y = int(round(norm_y * image_height))
                else:
                    px_x = int(round(x_raw))
                    px_y = int(round(y_raw))
                    norm_x = max(0.0, min(1.0, px_x / image_width))
                    norm_y = max(0.0, min(1.0, px_y / image_height))

                slots[slot_id] = {
                    "id": slot_id,
                    "name": project_label.name,
                    "x": round(norm_x, 4),
                    "y": round(norm_y, 4),
                    "x_px": px_x,
                    "y_px": px_y,
                    "confidence": round(conf, 4),
                    "visible": True,
                    "derived": False,
                }

    # Compute derived NECK (slot 1) from LEFT_SHOULDER & RIGHT_SHOULDER

    l_shoulder = slots[int(ProjectPoseLabel.LEFT_SHOULDER)]
    r_shoulder = slots[int(ProjectPoseLabel.RIGHT_SHOULDER)]

    if l_shoulder["visible"] and r_shoulder["visible"]:
        neck_norm_x = (l_shoulder["x"] + r_shoulder["x"]) / 2.0
        neck_norm_y = (l_shoulder["y"] + r_shoulder["y"]) / 2.0
        neck_px_x = int(round((l_shoulder["x_px"] + r_shoulder["x_px"]) / 2.0))
        neck_px_y = int(round((l_shoulder["y_px"] + r_shoulder["y_px"]) / 2.0))
        neck_conf = min(l_shoulder["confidence"], r_shoulder["confidence"])

        slots[int(ProjectPoseLabel.NECK)] = {
            "id": int(ProjectPoseLabel.NECK),
            "name": ProjectPoseLabel.NECK.name,
            "x": round(neck_norm_x, 4),
            "y": round(neck_norm_y, 4),
            "x_px": neck_px_x,
            "y_px": neck_px_y,
            "confidence": round(neck_conf, 4),
            "visible": True,
            "derived": True,
        }
    else:
        slots[int(ProjectPoseLabel.NECK)] = {
            "id": int(ProjectPoseLabel.NECK),
            "name": ProjectPoseLabel.NECK.name,
            "x": None,
            "y": None,
            "x_px": None,
            "y_px": None,
            "confidence": 0.0,
            "visible": False,
            "derived": True,
        }

    # Build final ordered list of 18 keypoints
    keypoints_list = [slots[i] for i in range(18)]
    valid_count = sum(1 for kpt in keypoints_list if kpt["visible"])

    return keypoints_list, valid_count
