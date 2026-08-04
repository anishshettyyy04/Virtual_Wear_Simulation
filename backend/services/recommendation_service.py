"""
Recommendation Service Layer
Virtual Wear Simulation — Phase 1.4 REST API
"""

try:
    from recommendation.engine import RecommendationEngine
except ImportError:
    from backend.recommendation.engine import RecommendationEngine


class RecommendationService:

    def __init__(self, engine=None):
        self.engine = engine or RecommendationEngine()

    def generate_recommendations(
        self,
        user_id,
        limit=10,
        force_refresh=False,
        selected_product_id=None,
        selected_category=None,
        selected_style=None,
        selected_color=None
    ):
        return self.engine.generate_recommendations(
            user_id=user_id,
            limit=limit,
            force_refresh=force_refresh,
            selected_product_id=selected_product_id,
            selected_category=selected_category,
            selected_style=selected_style,
            selected_color=selected_color
        )
