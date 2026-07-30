import pytest
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, Field

from app.config.settings import settings
from app.main import app

dummy_router = APIRouter(prefix="/dummy")


class DummyPayload(BaseModel):
    age: int = Field(..., gt=0)


@dummy_router.post("/validate")
async def dummy_validation_handler(payload: DummyPayload):
    return {"status": "ok"}


app.include_router(dummy_router, prefix=settings.API_V1_PREFIX)


@pytest.mark.asyncio
async def test_not_found_404_handler() -> None:
    """Verifies unknown endpoint returns 404 with standardized error payload."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get(f"{settings.API_V1_PREFIX}/nonexistent_endpoint")

    assert response.status_code == 404
    data = response.json()

    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert isinstance(data["error"]["message"], str)


@pytest.mark.asyncio
async def test_validation_error_422_handler() -> None:
    """Verifies invalid payload triggers 422 with VALIDATION_ERROR code."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post(
            f"{settings.API_V1_PREFIX}/dummy/validate",
            json={"age": -5},
        )

    assert response.status_code == 422
    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(data["error"]["message"], str)
