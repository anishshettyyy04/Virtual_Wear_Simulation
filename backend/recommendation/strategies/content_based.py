"""
Content-Based Vector Embedding Strategy Placeholder
Virtual Wear Simulation — Phase 1.3/2.0
"""

from .rule_based import BaseRecommendationStrategy


class ContentBasedStrategy(BaseRecommendationStrategy):
    """
    Placeholder strategy interface for TF-IDF / CLIP Vector Embedding Similarity Search.
    To be fully implemented in future ML phases.
    """

    def generate(self, user_preference, products, config=None, limit=10):
        raise NotImplementedError(
            "ContentBasedStrategy vector embeddings will be implemented in future ML phases. "
            "Use RuleBasedStrategy for Phase 1.3 execution."
        )
