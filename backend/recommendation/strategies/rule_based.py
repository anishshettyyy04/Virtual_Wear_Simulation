"""
Rule-Based Recommendation Strategy
Virtual Wear Simulation — Phase 1.3
"""

from abc import ABC, abstractmethod

from ..explain import RecommendationExplainer
from ..filters import apply_hard_filters
from ..scorer import RecommendationScorer


class BaseRecommendationStrategy(ABC):
    """Abstract base strategy interface for recommendation algorithms."""

    @abstractmethod
    def generate(self, user_preference, products, config=None, limit=10):
        """Generates ranked recommendations given user preferences and products dataset."""
        pass


class RuleBasedStrategy(BaseRecommendationStrategy):
    """
    Rule-Based recommendation strategy executing mandatory hard filters,
    configurable weighted attribute scoring, personalization boosts, and ranking.
    """

    def __init__(self, scorer=None, explainer=None):
        self.scorer = scorer or RecommendationScorer()
        self.explainer = explainer or RecommendationExplainer()

    def generate(self, user_preference, products, config=None, limit=10):
        """
        Executes rule-based scoring and filtering pipeline.
        Returns tuple: (ranked_recommendations, products_scanned_count, products_filtered_count)
        """
        products_scanned = len(products)
        products_filtered = 0
        candidates = []

        for product in products:
            # Hard filter evaluation
            passed, _ = apply_hard_filters(product, user_preference)
            if not passed:
                continue

            products_filtered += 1

            # Weighted attribute scoring with personalization boosts
            score, breakdown = self.scorer.calculate_score(product, user_preference, config=config)

            # Human-readable explanation generation
            reasons = self.explainer.generate_reasons(product, user_preference, breakdown)

            candidates.append({
                "productId": product.get('id'),
                "name": product.get('name'),
                "category": product.get('category'),
                "brand": product.get('brand'),
                "price": product.get('price'),
                "currency": product.get('currency', 'INR'),
                "image": product.get('image'),
                "rating": product.get('rating'),
                "score": score,
                "reasons": reasons
            })

        # O(n log n) ranking descending by normalized score with active category tie-breaker
        selected_cat = user_preference.get('selectedCategory')
        ranked = sorted(
            candidates,
            key=lambda x: (
                x['score'],
                1 if selected_cat and x['category'] == selected_cat else 0
            ),
            reverse=True
        )

        # Deduplication
        seen = set()
        unique_recs = []
        for item in ranked:
            if item['productId'] not in seen:
                seen.add(item['productId'])
                unique_recs.append(item)
            if len(unique_recs) >= limit:
                break

        return unique_recs, products_scanned, products_filtered
