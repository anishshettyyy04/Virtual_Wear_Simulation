"""
Core Recommendation Engine Interface with Caching, Versioning & Strategy Pattern
Virtual Wear Simulation — Phase 1.3 Optimization
"""

from datetime import datetime, timezone
import json
import os
import time

try:
    from cache.recommendation_cache import RecommendationCache
except ImportError:
    try:
        from backend.cache.recommendation_cache import RecommendationCache
    except ImportError:
        RecommendationCache = None

try:
    from recommendation.history import get_history_manager
except ImportError:
    try:
        from backend.recommendation.history import get_history_manager
    except ImportError:
        get_history_manager = lambda: None

try:
    from utils.logger import log_cache_event, logger
except ImportError:
    try:
        from backend.utils.logger import log_cache_event, logger
    except ImportError:
        import logging
        logger = logging.getLogger("virtual_wear")
        log_cache_event = lambda event_type, uid: None

from .strategies import RuleBasedStrategy


class RecommendationEngine:
    """
    Main Recommendation Engine orchestrating caching, config loading, strategy dispatching,
    history persistence, performance metrics collection, logging, and versioned JSON response formatting.
    """

    ENGINE_VERSION = "1.0.0"
    CONFIG_VERSION = "1.0"

    def __init__(self, products_file=None, users_file=None, config_file=None, strategy=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.products_file = products_file or os.path.join(base_dir, 'data', 'products.json')
        self.users_file = users_file or os.path.join(base_dir, 'data', 'user_preferences.json')
        self.config_file = config_file or os.path.join(base_dir, 'config', 'recommendation_config.json')

        self._products_cache = None
        self._users_cache = None
        self._config_cache = None

        self.strategy = strategy or RuleBasedStrategy()
        self.history_manager = get_history_manager()

        # Initialize Cache
        config = self._load_config()
        cache_cfg = config.get('cache', {})
        ttl = cache_cfg.get('ttlSeconds', 300)
        enabled = cache_cfg.get('enabled', True)
        self.cache = RecommendationCache(ttl_seconds=ttl, enabled=enabled) if RecommendationCache else None

    def _load_config(self, force_reload=False):
        """Loads recommendation configuration parameters."""
        if self._config_cache is None or force_reload:
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        self._config_cache = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to parse config file '{self.config_file}': {e}. Using defaults.")
                    self._config_cache = self._default_config()
            else:
                self._config_cache = self._default_config()
        return self._config_cache

    def _default_config(self):
        return {
            "weights": {"category": 35, "style": 20, "color": 15, "brand": 10, "fit": 10, "budget": 10},
            "boosts": {"wishlist": 15, "purchaseHistory": 10, "favoriteColor": 5, "climate": 5},
            "penalties": {"recommendationHistory": 10},
            "limits": {"maxRecommendations": 10},
            "cache": {"enabled": True, "ttlSeconds": 300}
        }

    def _load_data(self, force_reload=False):
        """Loads products and user preference datasets into memory cache."""
        if self._products_cache is None or force_reload:
            if not os.path.exists(self.products_file):
                logger.error(f"Products dataset missing at '{self.products_file}'")
                raise FileNotFoundError(f"Products dataset missing: {self.products_file}")
            with open(self.products_file, 'r', encoding='utf-8') as f:
                self._products_cache = json.load(f)

        if self._users_cache is None or force_reload:
            if not os.path.exists(self.users_file):
                logger.error(f"Users dataset missing at '{self.users_file}'")
                raise FileNotFoundError(f"Users dataset missing: {self.users_file}")
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_list = json.load(f)
                self._users_cache = {u['userId']: u for u in users_list}

    def get_user_preference(self, user_id):
        """Fetches user preference profile by user_id."""
        self._load_data()
        return self._users_cache.get(user_id)

    def generate_recommendations(self, user_id, limit=None, force_refresh=False):
        """
        Generates personalized product recommendations for user_id with cache lookup and versioning.

        Args:
            user_id (str): Target user identifier code.
            limit (int, optional): Maximum recommendations. Defaults to config limit.
            force_refresh (bool): If True, bypasses cache and recomputes score.

        Returns:
            dict: Versioned response envelope adhering to recommendation.schema.json.
        """
        start_time = time.perf_counter()
        strategy_name = getattr(self.strategy, '__class__', {}).__name__.replace("Strategy", "")

        # 1. Check Cache
        if self.cache and not force_refresh:
            cached_res = self.cache.get(user_id)
            if cached_res:
                log_cache_event("hit", user_id)
                # Update timing metric for cached retrieval
                cached_res["executionTimeMs"] = round((time.perf_counter() - start_time) * 1000, 2)
                return cached_res
            else:
                log_cache_event("miss", user_id)

        try:
            self._load_data()
            config = self._load_config()
        except Exception as err:
            exec_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "success": False,
                "message": f"Data loading error: {str(err)}",
                "engineVersion": self.ENGINE_VERSION,
                "strategy": strategy_name,
                "configVersion": self.CONFIG_VERSION,
                "executionTimeMs": exec_time_ms,
                "productsScanned": 0,
                "productsFiltered": 0,
                "recommendationsReturned": 0,
                "userId": str(user_id) if user_id else "unknown",
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "recommendations": []
            }

        user_preference = self._users_cache.get(user_id)
        if not user_preference:
            exec_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning(f"User ID '{user_id}' not found in user preferences dataset")
            return {
                "success": False,
                "message": f"User ID '{user_id}' not found",
                "engineVersion": self.ENGINE_VERSION,
                "strategy": strategy_name,
                "configVersion": self.CONFIG_VERSION,
                "executionTimeMs": exec_time_ms,
                "productsScanned": len(self._products_cache),
                "productsFiltered": 0,
                "recommendationsReturned": 0,
                "userId": str(user_id) if user_id else "unknown",
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "recommendations": []
            }

        rec_limit = limit if limit is not None else config.get('limits', {}).get('maxRecommendations', 10)

        # Delegate recommendation generation to strategy
        recommendations, scanned_count, filtered_count = self.strategy.generate(
            user_preference=user_preference,
            products=self._products_cache,
            config=config,
            limit=rec_limit
        )

        exec_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response_payload = {
            "success": True,
            "message": "Recommendations generated successfully",
            "engineVersion": self.ENGINE_VERSION,
            "strategy": strategy_name,
            "configVersion": self.CONFIG_VERSION,
            "executionTimeMs": exec_time_ms,
            "productsScanned": scanned_count,
            "productsFiltered": filtered_count,
            "recommendationsReturned": len(recommendations),
            "userId": user_id,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "recommendations": recommendations
        }

        # Store in Cache
        if self.cache:
            self.cache.set(user_id, response_payload)

        # Save History
        if self.history_manager:
            rec_pids = [r['productId'] for r in recommendations]
            self.history_manager.save_history(user_id, rec_pids)

        return response_payload


_global_engine = None


def recommend(user_id, limit=None, force_refresh=False, products_file=None, users_file=None, config_file=None, strategy=None):
    """Convenience functional interface for generating recommendations."""
    global _global_engine
    if _global_engine is None or products_file or users_file or config_file or strategy:
        _global_engine = RecommendationEngine(
            products_file=products_file,
            users_file=users_file,
            config_file=config_file,
            strategy=strategy
        )
    return _global_engine.generate_recommendations(user_id, limit=limit, force_refresh=force_refresh)
