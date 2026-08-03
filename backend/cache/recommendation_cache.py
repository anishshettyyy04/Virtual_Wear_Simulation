"""
In-Memory Recommendation Cache Subsystem
Virtual Wear Simulation — Phase 1.3 Optimization
"""

import time


class RecommendationCache:
    """
    In-memory caching layer with user_id key indexing, automatic TTL expiration,
    cache invalidation, and hit/miss statistics tracking.
    """

    def __init__(self, ttl_seconds=300, enabled=True):
        self.ttl_seconds = ttl_seconds
        self.enabled = enabled
        self._cache = {}
        self.hits = 0
        self.misses = 0

    def get(self, user_id):
        """
        Retrieves cached recommendations for user_id if valid and unexpired.
        Returns cached payload or None.
        """
        if not self.enabled:
            return None

        entry = self._cache.get(user_id)
        if not entry:
            self.misses += 1
            return None

        cached_time, value = entry
        if time.time() - cached_time > self.ttl_seconds:
            # Entry expired
            del self._cache[user_id]
            self.misses += 1
            return None

        self.hits += 1
        return value

    def set(self, user_id, recommendations):
        """
        Stores recommendations payload in cache for user_id with current timestamp.
        """
        if not self.enabled:
            return
        self._cache[user_id] = (time.time(), recommendations)

    def invalidate(self, user_id):
        """
        Invalidates cached entries for a specific user_id.
        """
        if user_id in self._cache:
            del self._cache[user_id]
            return True
        return False

    def clear(self):
        """
        Clears all cached entries and resets statistics.
        """
        self._cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self):
        """
        Returns dictionary of cache statistics including hit rate and entry counts.
        """
        total = self.hits + self.misses
        hit_rate = round((self.hits / total) * 100, 1) if total > 0 else 0.0
        return {
            "enabled": self.enabled,
            "ttlSeconds": self.ttl_seconds,
            "activeEntries": len(self._cache),
            "hits": self.hits,
            "misses": self.misses,
            "hitRatePercent": hit_rate
        }
