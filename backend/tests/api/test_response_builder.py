import json

from app.services.api.response_builder import ErrorCode, ResponseBuilder


def test_response_builder_success() -> None:
    """Verifies ResponseBuilder.success payload formatting and version metadata."""
    payload = ResponseBuilder.success(
        data={"result_id": "res_123"},
        message="Render complete",
        request_id="req_abc",
        request_duration_ms=120.45,
    )
    assert payload["success"] is True
    assert payload["api_version"] == "v1"
    assert payload["pipeline_version"] == "1.0.0"
    assert payload["engine_version"] == "1.0.0"
    assert payload["data"]["result_id"] == "res_123"
    assert payload["request_id"] == "req_abc"
    assert payload["request_duration_ms"] == 120.45


def test_response_builder_error() -> None:
    """Verifies ResponseBuilder.error JSONResponse construction and error codes."""
    response = ResponseBuilder.error(
        code=ErrorCode.WEIGHTS_MISSING,
        message="Model weights missing",
        status_code=503,
        request_id="req_err",
    )
    assert response.status_code == 503
    content = json.loads(response.body.decode("utf-8"))
    assert content["success"] is False
    assert content["error"]["code"] == ErrorCode.WEIGHTS_MISSING
    assert content["error"]["message"] == "Model weights missing"
    assert content["error"]["request_id"] == "req_err"
