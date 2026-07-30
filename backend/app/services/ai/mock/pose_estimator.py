from app.schemas.ai import PoseEstimationResult, PreprocessingResult
from app.services.ai.interfaces.pose_estimator import BasePoseEstimator
from app.utils.logger import logger


class MockPoseEstimator(BasePoseEstimator):
    """Deterministic mock pose estimator implementation."""

    async def estimate(
        self, preprocessed: PreprocessingResult
    ) -> PoseEstimationResult:
        logger.info(
            f"MockPoseEstimator: Estimating pose keypoints for person "
            f"'{preprocessed.person_processed_id}'"
        )
        return PoseEstimationResult(
            pose_id=f"pose_{preprocessed.person_processed_id}",
            pose_ref=f"mock://poses/pose_{preprocessed.person_processed_id}.json",
            keypoints_summary="33 landmark points aligned (shoulders, torso, arms)",
            num_keypoints=33,
            metadata={"estimator_name": "mock_pose", "confidence": 0.98},
        )
