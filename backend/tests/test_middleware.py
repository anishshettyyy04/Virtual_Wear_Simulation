import pytest
from httpx import ASGITransport, AsyncClient

from app.config.settings import settings
from app.main import app


@pytest.mark.asyncio
async def test_request_id_middleware_generated() -> None:
    """Verifies X-Request-ID header is generated if missing."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get(f"{settings.API_V1_PREFIX}/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


@pytest.mark.asyncio
async def test_request_id_middleware_propagated() -> None:
    """Verifies existing X-Request-ID header is preserved."""
    custom_id = "test-uuid-12345-67890"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get(
            f"{settings.API_V1_PREFIX}/health",
            headers={"X-Request-ID": custom_id},
        )

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id


@pytest.mark.asyncio
async def test_cors_middleware_allowed_origin() -> None:
    """Verifies CORS headers for allowed frontend origin."""
    origin = "http://localhost:5173"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.options(
            f"{settings.API_V1_PREFIX}/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
