import pytest
from httpx import ASGITransport, AsyncClient

from app.config.settings import settings
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint() -> None:
    """Verifies GET /api/v1/health returns 200 OK and HealthResponse structure."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get(f"{settings.API_V1_PREFIX}/health")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["status"] == "healthy"
    assert data["service"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
