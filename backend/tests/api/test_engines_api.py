from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_engines_endpoint() -> None:
    """Verifies GET /api/v1/engines discovers registered engines and metadata."""
    response = client.get("/api/v1/engines")
    assert response.status_code == 200
    json_resp = response.json()

    assert json_resp["success"] is True
    assert "data" in json_resp
    assert "engines" in json_resp["data"]
    assert json_resp["data"]["total_engines"] > 0

    engine_names = [e["name"] for e in json_resp["data"]["engines"]]
    assert "idm_vton" in engine_names


def test_ai_health_endpoint() -> None:
    """Verifies GET /api/v1/health/ai returns AI try-on readiness metrics."""
    response = client.get("/api/v1/health/ai")
    assert response.status_code == 200
    json_resp = response.json()

    assert json_resp["success"] is True
    assert "data" in json_resp
    assert "status" in json_resp["data"]
    assert "active_engine" in json_resp["data"]
    assert "device_info" in json_resp["data"]
