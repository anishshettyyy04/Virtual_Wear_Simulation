#!/usr/bin/env python3
"""
User Preference Dataset, Schema & Product Cross-Reference Validation Utility
Virtual Wear Simulation — Phase 1.2 Enhancements
"""

import json
import os
import re
import sys


def load_file(filepath):
    if not os.path.exists(filepath):
        print(f"ERROR: File not found at '{filepath}'")
        sys.exit(1)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_user_preference_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_data_path = os.path.join(base_dir, 'data', 'user_preferences.json')
    product_data_path = os.path.join(base_dir, 'data', 'products.json')
    schema_path = os.path.join(base_dir, 'schemas', 'user_preference.schema.json')

    user_profiles = load_file(user_data_path)
    products = load_file(product_data_path)
    schema = load_file(schema_path)

    valid_product_ids = set([p.get('id') for p in products])
    valid_product_categories = set([p.get('category') for p in products])

    total_users = len(user_profiles)
    print(f"Loaded {total_users} users\n")

    # 1. Unique User IDs Validation
    user_ids = [u.get('userId') for u in user_profiles]
    unique_user_ids = set(user_ids)
    if len(user_ids) != len(unique_user_ids):
        duplicates = [x for x in user_ids if user_ids.count(x) > 1]
        print(f"Unique IDs : FAIL (Duplicates found: {set(duplicates)})")
        sys.exit(1)
    else:
        print("Unique IDs : PASS\n")

    # 2. Schema & Extended Optional Field Validation
    required_fields = schema.get('required', [])
    enums = {
        'gender': schema['properties']['gender']['enum'],
        'ageGroup': schema['properties']['ageGroup']['enum'],
        'preferredFit': schema['properties']['preferredFit']['enum'],
        'budgetTier': schema['properties']['budgetTier']['enum'],
        'bodyType': schema['properties']['bodyType']['enum'],
        'preferredCategories': schema['properties']['preferredCategories']['items']['enum'],
        'preferredStyles': schema['properties']['preferredStyles']['items']['enum'],
        'preferredSeasons': schema['properties']['preferredSeasons']['items']['enum'],
        'climate': schema['properties']['climate']['enum'],
    }

    errors = []
    wishlist_errors = []
    purchase_errors = []
    category_compat_errors = []

    category_counts = {}
    style_counts = {}
    climate_counts = {}
    min_budgets = []
    max_budgets = []

    iso_timestamp_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

    for idx, user in enumerate(user_profiles):
        uid = user.get('userId', f'Index_{idx}')

        # Check required fields
        for field in required_fields:
            if field not in user:
                errors.append(f"[{uid}] Missing required field: '{field}'")

        # Check budget range constraints
        budget = user.get('budgetRange', {})
        b_min = budget.get('min', -1)
        b_max = budget.get('max', -1)
        if b_min < 0 or b_max <= b_min:
            errors.append(f"[{uid}] Invalid budgetRange: min={b_min}, max={b_max} (max must be > min >= 0)")
        else:
            min_budgets.append(b_min)
            max_budgets.append(b_max)

        # Check body metrics
        if user.get('height', 0) <= 0:
            errors.append(f"[{uid}] Invalid height: {user.get('height')} (must be > 0)")
        if user.get('weight', 0) <= 0:
            errors.append(f"[{uid}] Invalid weight: {user.get('weight')} (must be > 0)")

        # Check scalar enums
        for field in ['gender', 'ageGroup', 'preferredFit', 'budgetTier', 'bodyType']:
            if field in user and user[field] not in enums[field]:
                errors.append(f"[{uid}] Invalid {field}: '{user[field]}' (must be one of {enums[field]})")

        # Check optional climate enum
        if 'climate' in user and user['climate'] not in enums['climate']:
            errors.append(f"[{uid}] Invalid climate: '{user['climate']}' (must be one of {enums['climate']})")
        elif 'climate' in user:
            climate_counts[user['climate']] = climate_counts.get(user['climate'], 0) + 1

        # Check optional location object
        if 'location' in user:
            loc = user['location']
            if not isinstance(loc, dict) or not all(k in loc for k in ['country', 'state', 'city']):
                errors.append(f"[{uid}] Invalid location object: must contain country, state, city")

        # Check optional interactionMetrics object
        if 'interactionMetrics' in user:
            im = user['interactionMetrics']
            if not isinstance(im, dict) or any(im.get(k, -1) < 0 for k in ['productsViewed', 'productsLiked', 'productsPurchased']):
                errors.append(f"[{uid}] Invalid interactionMetrics: counts must be integers >= 0")

        # Check optional favoriteColorsFrequency object
        if 'favoriteColorsFrequency' in user:
            fcf = user['favoriteColorsFrequency']
            if not isinstance(fcf, dict) or any(not isinstance(v, int) or v < 0 for v in fcf.values()):
                errors.append(f"[{uid}] Invalid favoriteColorsFrequency: values must be integers >= 0")

        # Check optional lastPreferenceUpdate timestamp
        if 'lastPreferenceUpdate' in user and not iso_timestamp_pattern.match(user['lastPreferenceUpdate']):
            errors.append(f"[{uid}] Invalid lastPreferenceUpdate timestamp format")

        # Check array enums
        for field in ['preferredCategories', 'preferredStyles', 'preferredSeasons']:
            if field in user and isinstance(user[field], list):
                for val in user[field]:
                    if val not in enums[field]:
                        errors.append(f"[{uid}] Invalid element in {field}: '{val}' (must be one of {enums[field]})")

        # Check Wishlist Product Reference Integrity
        for pid in user.get('wishlist', []):
            if pid not in valid_product_ids:
                wishlist_errors.append(f"[{uid}] Wishlist item '{pid}' not found in products.json")

        # Check Purchase History Product Reference Integrity
        for pid in user.get('purchaseHistory', []):
            if pid not in valid_product_ids:
                purchase_errors.append(f"[{uid}] Purchase history item '{pid}' not found in products.json")

        # Check Category Compatibility with Phase 1.1
        for cat in user.get('preferredCategories', []):
            if cat not in valid_product_categories:
                category_compat_errors.append(f"[{uid}] Preferred category '{cat}' not found in products.json categories")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        for style in user.get('preferredStyles', []):
            style_counts[style] = style_counts.get(style, 0) + 1

    if errors:
        print("Schema Validation : FAIL")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("Schema Validation : PASS\n")

    if wishlist_errors:
        print("Wishlist References : FAIL")
        for err in wishlist_errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("Wishlist References : PASS\n")

    if purchase_errors:
        print("Purchase History : FAIL")
        for err in purchase_errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("Purchase History : PASS\n")

    if category_compat_errors:
        print("Category Compatibility : FAIL")
        for err in category_compat_errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("Category Compatibility : PASS\n")

    # 3. Preference Statistics Computation
    top_category = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[0]
    top_style = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[0]
    avg_min_budget = sum(min_budgets) / len(min_budgets) if min_budgets else 0
    avg_max_budget = sum(max_budgets) / len(max_budgets) if max_budgets else 0
    avg_mid_budget = (avg_min_budget + avg_max_budget) / 2

    print(f"Most Preferred Category : {top_category[0]} ({top_category[1]} users)\n")
    print(f"Most Preferred Style : {top_style[0]} ({top_style[1]} users)\n")
    print(f"Average Budget : INR {avg_mid_budget:.2f} (Min: INR {avg_min_budget:.2f}, Max: INR {avg_max_budget:.2f})\n")

    if climate_counts:
        top_climate = sorted(climate_counts.items(), key=lambda x: x[1], reverse=True)[0]
        print(f"Most Common Climate Zone : {top_climate[0]} ({top_climate[1]} users)\n")

    print("SUCCESS")


if __name__ == '__main__':
    validate_user_preference_data()
