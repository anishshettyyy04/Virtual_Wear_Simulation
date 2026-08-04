"""
Recommendation Engine Package
Virtual Wear Simulation — Phase 1.3
"""

from .engine import RecommendationEngine, recommend
from .filters import apply_hard_filters
from .scorer import RecommendationScorer
from .explain import RecommendationExplainer

__all__ = [
    'RecommendationEngine',
    'recommend',
    'apply_hard_filters',
    'RecommendationScorer',
    'RecommendationExplainer'
]
