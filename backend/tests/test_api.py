"""
API Router Production Integration Tests
Virtual Wear Simulation — Phase 1.4 Production
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure backend root is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from api.app import app
except ImportError:
    from backend.api.app import app


class TestBackendRESTAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_all_products_standard_response(self):
        """Test GET /api/v1/products returns standard BaseResponse structure."""
        response = self.client.get("/api/v1/products")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Request-ID", response.headers)

        res = response.json()
        self.assertTrue(res['success'])
        self.assertIn('message', res)
        self.assertIn('timestamp', res)
        self.assertIsNotNone(res['requestId'])
        self.assertIsInstance(res['data'], list)
        self.assertGreater(len(res['data']), 0)

    def test_get_products_filtered(self):
        """Test GET /api/v1/products with category filter."""
        response = self.client.get("/api/v1/products?category=tshirt")
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res['success'])
        for item in res['data']:
            self.assertEqual(item['category'], 'tshirt')

    def test_get_product_by_id_valid(self):
        """Test GET /api/v1/products/{productId} for existing product."""
        response = self.client.get("/api/v1/products/TS001")
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res['success'])
        self.assertEqual(res['data']['id'], 'TS001')

    def test_get_product_by_id_invalid(self):
        """Test GET /api/v1/products/{productId} for missing product returns 404 error envelope."""
        response = self.client.get("/api/v1/products/NON_EXISTENT_PROD")
        self.assertEqual(response.status_code, 404)
        res = response.json()
        self.assertFalse(res['success'])
        self.assertIn('not found', res['message'])
        self.assertIsNotNone(res['requestId'])

    def test_get_user_by_id_valid(self):
        """Test GET /api/v1/users/{userId} for existing user profile."""
        response = self.client.get("/api/v1/users/USR001")
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res['success'])
        self.assertEqual(res['data']['userId'], 'USR001')

    def test_get_user_by_id_invalid(self):
        """Test GET /api/v1/users/{userId} for missing user returns 404."""
        response = self.client.get("/api/v1/users/USR_NON_EXISTENT")
        self.assertEqual(response.status_code, 404)
        res = response.json()
        self.assertFalse(res['success'])

    def test_post_recommendations_valid(self):
        """Test POST /api/v1/recommendations for valid user request."""
        payload = {"userId": "USR001", "limit": 5}
        response = self.client.post("/api/v1/recommendations", json=payload)
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res['success'])
        self.assertIsNotNone(res['requestId'])
        rec_data = res['data']
        self.assertEqual(rec_data['userId'], 'USR001')
        self.assertEqual(rec_data['engineVersion'], '1.0.0')

    def test_post_recommendations_invalid_user(self):
        """Test POST /api/v1/recommendations for non-existent user returns 404."""
        payload = {"userId": "USR_NON_EXISTENT", "limit": 5}
        response = self.client.post("/api/v1/recommendations", json=payload)
        self.assertEqual(response.status_code, 404)

    def test_get_health(self):
        """Test GET /api/v1/health endpoint."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res['success'])
        self.assertIn(res['data']['status'], ['healthy', 'degraded'])

    def test_get_metrics(self):
        """Test GET /api/v1/metrics endpoint."""
        response = self.client.get("/api/v1/metrics")
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res['success'])
        self.assertIn('benchmarkSummary', res['data'])

    def test_openapi_documentation(self):
        """Test OpenAPI documentation availability."""
        res_docs = self.client.get("/docs")
        self.assertEqual(res_docs.status_code, 200)
        res_redoc = self.client.get("/redoc")
        self.assertEqual(res_redoc.status_code, 200)


if __name__ == '__main__':
    unittest.main()
