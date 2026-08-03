"""
Recommendation Explanation Module
Virtual Wear Simulation — Phase 1.3
"""


class RecommendationExplainer:
    """
    Generates human-readable, structured explanations for why a product was recommended.
    """

    @staticmethod
    def generate_reasons(product, user_preference, score_breakdown=None):
        """
        Generates list of clear, human-readable reason strings for the user.
        """
        reasons = []

        # Category Match
        preferred_cats = user_preference.get('preferredCategories', [])
        if product.get('category') in preferred_cats:
            reasons.append(f"Matches preferred category ({product.get('category')})")

        # Style Match
        preferred_styles = user_preference.get('preferredStyles', [])
        if product.get('style') in preferred_styles:
            reasons.append(f"Matches preferred style ({product.get('style')})")

        # Budget Check
        budget = user_preference.get('budgetRange', {})
        price = product.get('price', 0)
        b_min = budget.get('min', 0)
        b_max = budget.get('max', float('inf'))
        if b_min <= price <= b_max:
            reasons.append("Within your budget")

        # Color Match
        preferred_colors = [c.lower() for c in user_preference.get('preferredColors', [])]
        prod_colors = [c.lower() for c in product.get('colors', [])]
        matched_colors = set(preferred_colors).intersection(set(prod_colors))
        if matched_colors:
            color_str = ", ".join([c.title() for c in list(matched_colors)[:2]])
            reasons.append(f"Preferred color ({color_str})")

        # Brand Match
        preferred_brands = user_preference.get('preferredBrands', [])
        if product.get('brand') in preferred_brands:
            reasons.append(f"Favored brand ({product.get('brand')})")

        # Fit Match
        preferred_fit = user_preference.get('preferredFit')
        if product.get('fit') == preferred_fit:
            reasons.append(f"Matches preferred fit ({preferred_fit})")

        # Size Availability Match
        fav_sizes = user_preference.get('favoriteSizes', [])
        prod_sizes = product.get('sizes', [])
        matched_sizes = set([s.upper() for s in fav_sizes]).intersection(set([s.upper() for s in prod_sizes]))
        if matched_sizes:
            size_str = ", ".join(sorted(list(matched_sizes)))
            reasons.append(f"Available in your size ({size_str})")

        # Climate Match
        climate = user_preference.get('climate')
        if climate:
            reasons.append(f"Suitable for {climate} climate")

        # Wishlist Match
        pid = product.get('id')
        wishlist = user_preference.get('wishlist', [])
        if pid in wishlist:
            reasons.append("Item is in your wishlist")

        # High Customer Rating
        if product.get('rating', 0) >= 4.5:
            reasons.append(f"Highly rated product ({product.get('rating')}★)")

        return reasons if reasons else ["General recommendation based on catalog trends"]
