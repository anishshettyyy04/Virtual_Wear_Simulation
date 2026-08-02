import io
import os

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def create_test_image_bytes() -> bytes:
    """Helper generating dummy test image bytes."""
    img = Image.new("RGB", (200, 300), color=(120, 180, 240))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.api_smoke
@pytest.mark.skipif(
    os.getenv("RUN_REAL_API_TESTS") != "1",
    reason="Real API smoke test disabled unless RUN_REAL_API_TESTS=1",
)
def test_real_api_smoke_test() -> None:
    """Smoke test executing full HTTP API try-on inference when RUN_REAL_API_TESTS=1."""
    p_bytes = create_test_image_bytes()
    g_bytes = create_test_image_bytes()

    files = {
        "person_image": ("person.png", p_bytes, "image/png"),
        "garment_image": ("garment.png", g_bytes, "image/png"),
    }
    data = {
        "garment_category": "upper_body",
        "engine": "idm_vton",
    }

    response = client.post("/api/v1/tryon", files=files, data=data)
    assert response.status_code in (200, 503)  # 200 if weights present, 503 if missing

    json_resp = response.json()
    assert "success" in json_resp
    assert "api_version" in json_resp
