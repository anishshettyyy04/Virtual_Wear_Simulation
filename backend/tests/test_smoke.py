"""
Automated Smoke Test Suite
Virtual Wear Simulation — Phase 1.5 Finalization
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from api.app import app
except ImportError:
    from backend.api.app import app


class TestBackendSmoke(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def _assert_base_envelope(self, response_json, expected_success=True):
        self.assertIn("success", response_json)
        self.assertEqual(response_json["success"], expected_success)
        self.assertIn("message", response_json)
        self.assertIn("timestamp", response_json)
        self.assertIn("requestId", response_json)
        self.assertIsNotNone(response_json["requestId"])

    def test_smoke_products_list(self):
        res = self.client.get("/api/v1/products")
        self.assertEqual(res.status_code, 200)
        self.assertIn("X-Request-ID", res.headers)
        body = res.json()
        self._assert_base_envelope(body, expected_success=True)
        self.assertIsInstance(body["data"], list)

    def test_smoke_product_detail(self):
        res = self.client.get("/api/v1/products/TS001")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self._assert_base_envelope(body, expected_success=True)
        self.assertEqual(body["data"]["id"], "TS001")

    def test_smoke_product_not_found(self):
        res = self.client.get("/api/v1/products/INVALID_PRODUCT_ID")
        self.assertEqual(res.status_code, 404)
        body = res.json()
        self._assert_base_envelope(body, expected_success=False)

    def test_smoke_user_profile(self):
        res = self.client.get("/api/v1/users/USR001")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self._assert_base_envelope(body, expected_success=True)
        self.assertEqual(body["data"]["userId"], "USR001")

    def test_smoke_recommendations(self):
        res = self.client.post("/api/v1/recommendations", json={"userId": "USR001", "limit": 5})
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self._assert_base_envelope(body, expected_success=True)
        self.assertEqual(body["data"]["userId"], "USR001")
        self.assertGreater(len(body["data"]["recommendations"]), 0)

    def test_smoke_health(self):
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self._assert_base_envelope(body, expected_success=True)
        self.assertIn(body["data"]["status"], ["healthy", "degraded"])

    def test_smoke_metrics(self):
        res = self.client.get("/api/v1/metrics")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self._assert_base_envelope(body, expected_success=True)
        self.assertIn("benchmarkSummary", body["data"])


if __name__ == '__main__':
    unittest.main()
