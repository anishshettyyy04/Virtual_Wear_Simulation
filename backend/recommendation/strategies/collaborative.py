"""
Collaborative Filtering Strategy Placeholder
Virtual Wear Simulation — Phase 1.3/2.0
"""

from .rule_based import BaseRecommendationStrategy


class CollaborativeStrategy(BaseRecommendationStrategy):
    """
    Placeholder strategy interface for Matrix Factorization / User-User KNN Collaborative Filtering.
    To be fully implemented in future ML phases.
    """

    def generate(self, user_preference, products, config=None, limit=10):
        raise NotImplementedError(
            "CollaborativeStrategy is a future ML capability. "
            "Use RuleBasedStrategy for Phase 1.3 execution."
        )
