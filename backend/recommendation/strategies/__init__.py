"""
Recommendation Strategies Subsystem
Virtual Wear Simulation — Phase 1.3
"""

from .rule_based import RuleBasedStrategy, BaseRecommendationStrategy
from .collaborative import CollaborativeStrategy
from .content_based import ContentBasedStrategy
from .hybrid import HybridStrategy

__all__ = [
    'BaseRecommendationStrategy',
    'RuleBasedStrategy',
    'CollaborativeStrategy',
    'ContentBasedStrategy',
    'HybridStrategy'
]
