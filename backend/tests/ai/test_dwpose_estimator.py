import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app.schemas.ai import PreprocessingResult
from app.services.ai.exceptions import PoseEstimationError
from app.services.ai.pose.dwpose_estimator import DWPoseEstimator


class FakeONNXDetectorSession:
    """Fake ONNX Detector session for offline testing."""

    def __call__(self, image: Image.Image):
        w, h = image.size
        # Return two bounding boxes: box1 (small area), box2 (large area)
        box1 = np.array([10.0, 10.0, 50.0, 50.0], dtype=np.float32)  # area 1600
        score1 = 0.95

        box2 = np.array([20.0, 20.0, 400.0, 400.0], dtype=np.float32)  # area 144400
        score2 = 0.98

        boxes = np.stack([box1, box2], axis=0)
        scores = np.array([score1, score2], dtype=np.float32)
        return boxes, scores


class FakeONNXNoPersonSession:
    """Fake ONNX Detector session returning no valid person scores."""

    def __call__(self, image: Image.Image):
        boxes = np.array([[10.0, 10.0, 50.0, 50.0]], dtype=np.float32)
        scores = np.array([0.1], dtype=np.float32)  # Below threshold 0.4
        return boxes, scores


class FakeONNXPoseSession:
    """Fake ONNX Pose session returning 17 COCO keypoints."""

    def __call__(self, image: Image.Image, box: np.ndarray):
        raw_kpts = np.zeros((17, 3), dtype=np.float32)
        # Set Nose (0), L_Shoulder (5), R_Shoulder (6)
        raw_kpts[0] = [0.5, 0.2, 0.95]
        raw_kpts[5] = [0.6, 0.3, 0.90]
        raw_kpts[6] = [0.4, 0.3, 0.85]
        return raw_kpts


@pytest.fixture
def fake_person_image(tmp_path: Path) -> Path:
    img_path = tmp_path / "processed_person.jpg"
    img = Image.new("RGB", (500, 500), color=(200, 200, 200))
    img.save(img_path, format="JPEG")
    return img_path


@pytest.mark.asyncio
async def test_dwpose_estimator_fake_inference(fake_person_image: Path, tmp_path: Path):
    """Test DWPoseEstimator with fake detector & pose sessions."""
    output_dir = tmp_path / "poses"

    estimator = DWPoseEstimator(
        device="cpu",
        confidence_threshold=0.3,
        detection_threshold=0.4,
        output_dir=str(output_dir),
        detector_session=FakeONNXDetectorSession(),
        pose_session=FakeONNXPoseSession(),
    )

    preprocessed = PreprocessingResult(
        person_processed_id="person_test_001",
        garment_processed_id="garment_test_001",
        person_image_ref=str(fake_person_image),
        garment_image_ref=str(fake_person_image),
    )

    result = await estimator.estimate(preprocessed)

    assert result.pose_id.startswith("pose_person_test_001_")
    assert result.num_keypoints == 4  # Nose, L_Shoulder, R_Shoulder, Neck
    assert Path(result.pose_ref).exists()

    # Read saved JSON artifact
    with open(result.pose_ref, "r", encoding="utf-8") as f:
        artifact = json.load(f)

    assert artifact["schema_version"] == "v1"
    assert artifact["topology"] == "COCO_18"
    assert len(artifact["keypoints"]) == 18
    assert artifact["num_keypoints_detected"] == 4
    # Selected bounding box should be box2 (largest area)
    assert artifact["person"]["bbox"]["width"] == 380.0
    assert artifact["person"]["bbox"]["height"] == 380.0


@pytest.mark.asyncio
async def test_dwpose_estimator_no_person_detected(
    fake_person_image: Path, tmp_path: Path
):
    """Test controlled failure when no valid person is detected."""
    estimator = DWPoseEstimator(
        device="cpu",
        detection_threshold=0.4,
        output_dir=str(tmp_path / "poses"),
        detector_session=FakeONNXNoPersonSession(),
        pose_session=FakeONNXPoseSession(),
    )

    preprocessed = PreprocessingResult(
        person_processed_id="noperson_001",
        garment_processed_id="garment_001",
        person_image_ref=str(fake_person_image),
        garment_image_ref=str(fake_person_image),
    )

    with pytest.raises(
        PoseEstimationError, match="No valid human pose detected in image."
    ):
        await estimator.estimate(preprocessed)


@pytest.mark.asyncio
async def test_dwpose_estimator_path_traversal_containment(
    fake_person_image: Path, tmp_path: Path
):
    """Verify malicious IDs cannot escape output directory via path traversal."""
    output_dir = tmp_path / "poses"
    estimator = DWPoseEstimator(
        device="cpu",
        output_dir=str(output_dir),
        detector_session=FakeONNXDetectorSession(),
        pose_session=FakeONNXPoseSession(),
    )

    malicious_id = "../../../etc/passwd"
    preprocessed = PreprocessingResult(
        person_processed_id=malicious_id,
        garment_processed_id="garment_001",
        person_image_ref=str(fake_person_image),
        garment_image_ref=str(fake_person_image),
    )

    result = await estimator.estimate(preprocessed)

    artifact_path = Path(result.pose_ref)
    assert artifact_path.parent.resolve() == output_dir.resolve()
    assert "passwd" in artifact_path.name
