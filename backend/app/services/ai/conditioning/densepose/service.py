from app.services.ai.conditioning.base import (
    BaseDensePoseService,
    DensePoseResult,
)


class MockDensePoseService(BaseDensePoseService):
    """Mock implementation of BaseDensePoseService for pipeline testing."""

    async def process(self, person_image_ref: str) -> DensePoseResult:
        """Returns mock DensePoseResult without running inference."""
        raise NotImplementedError
