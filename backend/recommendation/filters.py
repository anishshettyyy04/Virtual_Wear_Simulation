"""
Recommendation Hard Filters Module
Virtual Wear Simulation — Phase 1.3
"""


def filter_by_category(product, preferred_categories):
    """Return True if product category matches user preferred categories."""
    if not preferred_categories:
        return True
    return product.get('category') in preferred_categories


def filter_by_budget(product, budget_range):
    """Return True if product price falls within user min and max budget."""
    if not budget_range or not isinstance(budget_range, dict):
        return True
    price = product.get('price', 0)
    min_budget = budget_range.get('min', 0)
    max_budget = budget_range.get('max', float('inf'))
    return min_budget <= price <= max_budget


def filter_by_color(product, preferred_colors):
    """Return True if product shares at least one color with user preferred colors."""
    if not preferred_colors:
        return True
    product_colors = product.get('colors', [])
    preferred_set = set([c.lower() for c in preferred_colors])
    product_set = set([c.lower() for c in product_colors])
    return bool(preferred_set.intersection(product_set))


def filter_by_brand(product, preferred_brands):
    """Return True if product brand is in user preferred brands."""
    if not preferred_brands:
        return True
    return product.get('brand') in preferred_brands


def filter_by_size(product, favorite_sizes):
    """Return True if product has at least one size matching user favorite sizes."""
    if not favorite_sizes:
        return True
    product_sizes = product.get('sizes', [])
    fav_set = set([s.upper() for s in favorite_sizes])
    prod_set = set([s.upper() for s in product_sizes])
    return bool(fav_set.intersection(prod_set))


def filter_by_season(product, preferred_seasons):
    """Return True if product season matches user preferred seasons or is all-season."""
    if not preferred_seasons:
        return True
    prod_season = product.get('season')
    if prod_season == 'all-season':
        return True
    return prod_season in preferred_seasons or 'all-season' in preferred_seasons


def filter_by_gender(product, user_gender):
    """Return True if product gender matches user gender or is unisex."""
    if not user_gender:
        return True
    prod_gender = product.get('gender')
    if prod_gender == 'unisex' or user_gender == 'unisex':
        return True
    return prod_gender == user_gender


def filter_by_availability(product):
    """Return True if product is available and stock > 0."""
    return bool(product.get('isAvailable', True)) and product.get('stock', 0) > 0


def apply_hard_filters(product, user_preference):
    """
    Applies mandatory criteria to determine if product is eligible for scoring.
    Must satisfy availability, gender compatibility, and budget boundaries.
    """
    if not filter_by_availability(product):
        return False, "Not available in stock"

    if not filter_by_gender(product, user_preference.get('gender')):
        return False, "Gender mismatch"

    if not filter_by_budget(product, user_preference.get('budgetRange')):
        return False, "Out of budget range"

    return True, "Passed hard filters"
