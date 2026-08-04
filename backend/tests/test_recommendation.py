"""
Expanded Unit Tests for Recommendation Engine Subsystem
Virtual Wear Simulation — Phase 1.3 Optimization
"""

import json
import os
import sys
import tempfile
import time
import unittest

# Ensure backend root is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cache.recommendation_cache import RecommendationCache
from recommendation.analytics import (
    compute_average_recommendation_score,
    compute_category_popularity,
    compute_most_recommended_products,
    compute_recommendation_frequency,
    compute_user_preference_distribution
)
from recommendation.engine import RecommendationEngine, recommend
from recommendation.filters import apply_hard_filters, filter_by_budget, filter_by_category
from recommendation.health import check_system_health
from recommendation.history import RecommendationHistoryManager
from recommendation.scorer import RecommendationScorer
from recommendation.strategies import CollaborativeStrategy, RuleBasedStrategy
from scripts.benchmark_recommendation import run_benchmark


class TestRecommendationEngineOptimization(unittest.TestCase):

    def setUp(self):
        self.engine = RecommendationEngine()
        self.scorer = RecommendationScorer()

    def test_valid_user_recommendations_and_versioning(self):
        """Test generating recommendations with versioning metadata."""
        res = self.engine.generate_recommendations("USR001", limit=5)
        self.assertTrue(res['success'])
        self.assertEqual(res['userId'], "USR001")
        self.assertEqual(res['engineVersion'], "1.0.0")
        self.assertEqual(res['strategy'], "RuleBased")
        self.assertEqual(res['configVersion'], "1.0")
        self.assertIn('generatedAt', res)
        self.assertGreaterEqual(res['executionTimeMs'], 0.0)
        self.assertGreater(res['recommendationsReturned'], 0)
        self.assertLessEqual(len(res['recommendations']), 5)

    def test_invalid_user_handling(self):
        """Test graceful handling when an invalid user ID is supplied."""
        res = self.engine.generate_recommendations("USR_NON_EXISTENT", limit=5)
        self.assertFalse(res['success'])
        self.assertEqual(res['recommendationsReturned'], 0)
        self.assertEqual(res['recommendations'], [])
        self.assertIn('message', res)

    def test_budget_filtering(self):
        """Test that all recommended products strictly respect user budget limits."""
        res = self.engine.generate_recommendations("USR001", limit=10)
        user_pref = self.engine.get_user_preference("USR001")
        b_min = user_pref['budgetRange']['min']
        b_max = user_pref['budgetRange']['max']

        for item in res['recommendations']:
            price = item['price']
            self.assertTrue(
                b_min <= price <= b_max,
                f"Product price {price} outside budget range [{b_min}, {b_max}]"
            )

    def test_cache_operations_and_ttl(self):
        """Test in-memory cache set, get, hit/miss stats, and TTL expiration."""
        cache = RecommendationCache(ttl_seconds=1, enabled=True)

        payload = {"test": "data"}
        cache.set("USR_TEST", payload)

        # Test Hit
        retrieved = cache.get("USR_TEST")
        self.assertEqual(retrieved, payload)

        stats = cache.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 0)

        # Test Invalidation
        cache.invalidate("USR_TEST")
        self.assertIsNone(cache.get("USR_TEST"))

        # Test Expiration
        cache.set("USR_TEST_EXPIRE", payload)
        time.sleep(1.1)
        self.assertIsNone(cache.get("USR_TEST_EXPIRE"))

    def test_health_check_module(self):
        """Test health check monitoring module."""
        health = check_system_health(self.engine)
        self.assertIn(health['status'], ['healthy', 'degraded'])
        self.assertEqual(health['products'], 'loaded')
        self.assertEqual(health['users'], 'loaded')
        self.assertEqual(health['configuration'], 'loaded')
        self.assertEqual(health['strategy'], 'RuleBased')
        self.assertEqual(health['cache'], 'enabled')

    def test_history_manager_operations(self):
        """Test recommendation history saving, loading, and clearing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_history_file = f.name

        try:
            hm = RecommendationHistoryManager(storage_file=temp_history_file)
            hm.save_history("USR_HIST", ["TS001", "JN001"])

            loaded = hm.load_history("USR_HIST")
            self.assertIn("TS001", loaded)
            self.assertIn("JN001", loaded)

            hm.clear_history("USR_HIST")
            self.assertEqual(hm.load_history("USR_HIST"), [])
        finally:
            if os.path.exists(temp_history_file):
                os.remove(temp_history_file)

    def test_benchmark_execution_and_metrics_export(self):
        """Test benchmark execution and metrics JSON file export."""
        run_benchmark()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        metrics_file = os.path.join(base_dir, 'data', 'recommendation_metrics.json')

        self.assertTrue(os.path.exists(metrics_file))
        with open(metrics_file, 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)

        self.assertIn('benchmarkSummary', metrics_data)
        self.assertIn('analytics', metrics_data)
        self.assertGreater(metrics_data['benchmarkSummary']['usersTested'], 0)

    def test_score_ranking_and_normalization(self):
        """Test that scores are normalized to [0, 100] and ranked in descending order."""
        res = self.engine.generate_recommendations("USR002", limit=10)
        recs = res['recommendations']

        scores = [r['score'] for r in recs]
        for score in scores:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 100.0)

        sorted_scores = sorted(scores, reverse=True)
        self.assertEqual(scores, sorted_scores)

    def test_no_duplicate_recommendations(self):
        """Test that output contains no duplicate product IDs."""
        res = self.engine.generate_recommendations("USR004", limit=10)
        rec_ids = [r['productId'] for r in res['recommendations']]
        self.assertEqual(len(rec_ids), len(set(rec_ids)))

    def test_guest_session_fallback_identity(self):
        """Test that dynamic guest session IDs resolve to fallback preferences cleanly."""
        res = self.engine.generate_recommendations("GUEST_SESSION_TEST_123", limit=5)
        self.assertTrue(res['success'])
        self.assertEqual(res['userId'], "GUEST_SESSION_TEST_123")
        self.assertGreater(len(res['recommendations']), 0)

    def test_context_aware_recommendation_personalization(self):
        """Test that recommendation scoring adjusts based on active garment context."""
        res_tshirt = self.engine.generate_recommendations(
            "GUEST_SESSION_CTX", limit=5, selected_category="tshirt"
        )
        res_jeans = self.engine.generate_recommendations(
            "GUEST_SESSION_CTX", limit=5, selected_category="jeans"
        )

        top_tshirt_cat = res_tshirt['recommendations'][0]['category']
        top_jeans_cat = res_jeans['recommendations'][0]['category']

        self.assertEqual(top_tshirt_cat, "tshirt")
        self.assertEqual(top_jeans_cat, "jeans")

    def test_composite_cache_key_isolation(self):
        """Test that composite cache keys isolate recommendations by context."""
        cache = RecommendationCache(ttl_seconds=300, enabled=True)
        engine = RecommendationEngine()
        engine.cache = cache

        res1 = engine.generate_recommendations("GUEST_CACHE", selected_category="tshirt")
        res2 = engine.generate_recommendations("GUEST_CACHE", selected_category="jeans")

        self.assertEqual(cache.get_stats()['activeEntries'], 2)


if __name__ == '__main__':
    unittest.main()
