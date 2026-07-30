from app.services.ai.interfaces.human_parser import BaseHumanParser
from app.services.ai.interfaces.pose_estimator import BasePoseEstimator
from app.services.ai.interfaces.postprocessor import BasePostprocessor
from app.services.ai.interfaces.preprocessor import BasePreprocessor
from app.services.ai.interfaces.tryon_engine import BaseTryOnEngine
from app.services.ai.mock.human_parser import MockHumanParser
from app.services.ai.mock.pose_estimator import MockPoseEstimator
from app.services.ai.mock.postprocessor import MockPostprocessor
from app.services.ai.mock.preprocessor import MockPreprocessor
from app.services.ai.mock.tryon_engine import MockTryOnEngine


def test_mock_stage_implementations_satisfy_interfaces() -> None:
    """Verifies mock stage implementations inherit from abstract interfaces."""
    assert isinstance(MockPreprocessor(), BasePreprocessor)
    assert isinstance(MockHumanParser(), BaseHumanParser)
    assert isinstance(MockPoseEstimator(), BasePoseEstimator)
    assert isinstance(MockTryOnEngine(), BaseTryOnEngine)
    assert isinstance(MockPostprocessor(), BasePostprocessor)
