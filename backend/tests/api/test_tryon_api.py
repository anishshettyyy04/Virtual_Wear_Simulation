import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def create_dummy_image_bytes(width: int = 100, height: int = 100) -> bytes:
    """Helper generating dummy PNG image bytes."""
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_tryon_endpoint_success() -> None:
    """Verifies POST /api/v1/tryon route executes successfully."""
    p_bytes = create_dummy_image_bytes(200, 300)
    g_bytes = create_dummy_image_bytes(200, 300)

    files = {
        "person_image": ("person.png", p_bytes, "image/png"),
        "garment_image": ("garment.png", g_bytes, "image/png"),
    }
    data = {
        "garment_category": "upper_body",
        "engine": "idm_vton",
    }

    response = client.post("/api/v1/tryon", files=files, data=data)
    assert response.status_code == 200, f"Error: {response.json()}"
    json_resp = response.json()

    assert json_resp["success"] is True
    assert "data" in json_resp
    assert json_resp["data"]["engine"] == "idm_vton"
    assert json_resp["data"]["garment_category"] == "upper_body"
    assert "request_id" in json_resp
    assert "request_duration_ms" in json_resp


def test_tryon_endpoint_invalid_category() -> None:
    """Verifies POST /api/v1/tryon route rejects invalid garment categories with 422."""
    p_bytes = create_dummy_image_bytes()
    g_bytes = create_dummy_image_bytes()

    files = {
        "person_image": ("person.png", p_bytes, "image/png"),
        "garment_image": ("garment.png", g_bytes, "image/png"),
    }
    data = {
        "garment_category": "invalid_category",
        "engine": "idm_vton",
    }

    response = client.post("/api/v1/tryon", files=files, data=data)
    assert response.status_code == 422
    json_resp = response.json()
    assert json_resp["success"] is False
    assert json_resp["error"]["code"] == "INVALID_CATEGORY"


def test_tryon_endpoint_unsupported_engine() -> None:
    """Verifies POST /api/v1/tryon route rejects unregistered engine names with 422."""
    p_bytes = create_dummy_image_bytes()
    g_bytes = create_dummy_image_bytes()

    files = {
        "person_image": ("person.png", p_bytes, "image/png"),
        "garment_image": ("garment.png", g_bytes, "image/png"),
    }
    data = {
        "garment_category": "upper_body",
        "engine": "non_existent_engine",
    }

    response = client.post("/api/v1/tryon", files=files, data=data)
    assert response.status_code == 422
    json_resp = response.json()
    assert json_resp["success"] is False
    assert json_resp["error"]["code"] == "INVALID_ENGINE"
