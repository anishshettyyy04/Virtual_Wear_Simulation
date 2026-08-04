"""
Recommendation Scoring Module
Virtual Wear Simulation — Phase 1.3
"""


class RecommendationScorer:
    """
    Weighted attribute scoring engine for clothing recommendations.
    Applies configurable attribute weights and personalization boosts/penalties.
    Normalizes output to [0, 100].
    """

    DEFAULT_WEIGHTS = {
        'category': 35.0,
        'style': 20.0,
        'color': 15.0,
        'brand': 10.0,
        'fit': 10.0,
        'budget': 10.0
    }

    DEFAULT_BOOSTS = {
        'wishlist': 15.0,
        'purchaseHistory': 10.0,
        'favoriteColor': 5.0,
        'climate': 5.0,
        'rating': 5.0
    }

    DEFAULT_PENALTIES = {
        'recommendationHistory': 10.0
    }

    CLIMATE_MATERIAL_MAP = {
        'tropical': ['cotton', 'linen', 'viscose', 'georgette'],
        'coastal': ['cotton', 'linen', 'viscose'],
        'cold': ['fleece', 'nylon', 'leather', 'wool'],
        'desert': ['cotton', 'linen', 'silk'],
        'temperate': ['cotton', 'denim', 'polyester']
    }

    def __init__(self, weights=None, boosts=None, penalties=None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.boosts = boosts or self.DEFAULT_BOOSTS
        self.penalties = penalties or self.DEFAULT_PENALTIES

    def calculate_score(self, product, user_preference, config=None):
        """
        Calculates normalized recommendation score (0 - 100) for a product.
        Returns (score, score_breakdown).
        """
        weights = config.get('weights', self.weights) if config else self.weights
        boosts_cfg = config.get('boosts', self.boosts) if config else self.boosts
        penalties_cfg = config.get('penalties', self.penalties) if config else self.penalties

        breakdown = {}

        # 1. Category Score
        preferred_cats = user_preference.get('preferredCategories', [])
        w_cat = float(weights.get('category', 35))
        if product.get('category') in preferred_cats:
            breakdown['category'] = w_cat
        else:
            breakdown['category'] = 0.0

        # Primary Active Category Context Boost
        selected_cat = user_preference.get('selectedCategory')
        if selected_cat and product.get('category') == selected_cat:
            breakdown['context_category_boost'] = 40.0

        # 2. Style Score
        preferred_styles = user_preference.get('preferredStyles', [])
        w_style = float(weights.get('style', 20))
        if product.get('style') in preferred_styles:
            breakdown['style'] = w_style
        else:
            breakdown['style'] = 0.0

        # 3. Color Score
        preferred_colors = [c.lower() for c in user_preference.get('preferredColors', [])]
        color_freq = user_preference.get('favoriteColorsFrequency', {})
        prod_colors = [c.lower() for c in product.get('colors', [])]

        w_color = float(weights.get('color', 15))
        matched_colors = set(preferred_colors).intersection(set(prod_colors))
        if matched_colors:
            color_match_ratio = len(matched_colors) / max(len(preferred_colors), 1)
            fav_bonus = float(boosts_cfg.get('favoriteColor', 5.0))
            freq_bonus = sum(color_freq.get(c, 0) for c in matched_colors) / 50.0
            breakdown['color'] = min(w_color, (color_match_ratio * (w_color - fav_bonus)) + min(freq_bonus, fav_bonus))
        else:
            breakdown['color'] = 0.0

        # 4. Brand Score
        preferred_brands = user_preference.get('preferredBrands', [])
        w_brand = float(weights.get('brand', 10))
        if product.get('brand') in preferred_brands:
            breakdown['brand'] = w_brand
        else:
            breakdown['brand'] = 0.0

        # 5. Fit Score
        preferred_fit = user_preference.get('preferredFit')
        w_fit = float(weights.get('fit', 10))
        if product.get('fit') == preferred_fit:
            breakdown['fit'] = w_fit
        else:
            breakdown['fit'] = 0.0

        # 6. Budget Score
        budget = user_preference.get('budgetRange', {})
        price = product.get('price', 0)
        b_min = budget.get('min', 0)
        b_max = budget.get('max', price)
        w_budget = float(weights.get('budget', 10))

        if b_min <= price <= b_max:
            mid = (b_min + b_max) / 2.0
            range_span = (b_max - b_min) / 2.0 if b_max > b_min else 1.0
            distance = abs(price - mid) / range_span
            breakdown['budget'] = w_budget * (1.0 - (0.5 * distance))
        else:
            breakdown['budget'] = 0.0

        base_score = sum(breakdown.values())

        # --- Advanced Personalization Boosts & Penalties ---
        boosts_total = 0.0
        pid = product.get('id')

        # Wishlist boost
        b_wishlist = float(boosts_cfg.get('wishlist', 15))
        if pid in user_preference.get('wishlist', []):
            boosts_total += b_wishlist
            breakdown['wishlist_boost'] = b_wishlist

        # Purchase history boost
        b_purchase = float(boosts_cfg.get('purchaseHistory', 10))
        if user_preference.get('purchaseHistory', []):
            boosts_total += b_purchase / 2.0
            breakdown['purchase_history_boost'] = b_purchase / 2.0

        # Climate alignment boost
        b_climate = float(boosts_cfg.get('climate', 5))
        climate = user_preference.get('climate')
        if climate and climate in self.CLIMATE_MATERIAL_MAP:
            allowed_mats = self.CLIMATE_MATERIAL_MAP[climate]
            prod_mat = product.get('material', '').lower()
            if any(m in prod_mat for m in allowed_mats):
                boosts_total += b_climate
                breakdown['climate_boost'] = b_climate

        # Recommendation history penalty
        p_history = float(penalties_cfg.get('recommendationHistory', 10))
        if pid in user_preference.get('recommendationHistory', []):
            boosts_total -= p_history
            breakdown['history_penalty'] = -p_history

        # Rating bonus
        b_rating = float(boosts_cfg.get('rating', 5))
        if product.get('rating', 0) >= 4.5:
            boosts_total += b_rating
            breakdown['rating_boost'] = b_rating

        raw_total = base_score + boosts_total
        normalized_score = round(max(0.0, min(100.0, raw_total)), 1)

        return normalized_score, breakdown
