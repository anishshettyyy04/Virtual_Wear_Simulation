"""
Hybrid Recommendation Strategy Placeholder
Virtual Wear Simulation — Phase 1.3/2.0
"""

from .rule_based import BaseRecommendationStrategy


class HybridStrategy(BaseRecommendationStrategy):
    """
    Placeholder strategy interface combining Rule-Based, Collaborative, and Content-Based scoring models.
    To be fully implemented in future ML phases.
    """

    def generate(self, user_preference, products, config=None, limit=10):
        raise NotImplementedError(
            "HybridStrategy model ensemble will be implemented in future ML phases. "
            "Use RuleBasedStrategy for Phase 1.3 execution."
        )
