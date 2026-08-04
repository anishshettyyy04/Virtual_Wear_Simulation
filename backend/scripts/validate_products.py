#!/usr/bin/env python3
"""
Product Dataset & Schema Validation Utility
Virtual Wear Simulation — Phase 1.1
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


def validate_product_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'products.json')
    schema_path = os.path.join(base_dir, 'schemas', 'product.schema.json')

    products = load_file(data_path)
    schema = load_file(schema_path)

    total_products = len(products)
    print(f"Loaded {total_products} products\n")

    # 1. Unique IDs Validation
    ids = [p.get('id') for p in products]
    unique_ids = set(ids)
    if len(ids) != len(unique_ids):
        duplicates = [x for x in ids if ids.count(x) > 1]
        print(f"Unique IDs: FAIL (Duplicates found: {set(duplicates)})")
        sys.exit(1)
    else:
        print("Unique IDs: PASS\n")

    # 2. Schema Validation
    required_fields = schema.get('required', [])
    enums = {
        k: v['enum']
        for k, v in schema.get('properties', {}).items()
        if 'enum' in v
    }

    errors = []
    category_counts = {}

    for idx, product in enumerate(products):
        pid = product.get('id', f'Index_{idx}')
        cat = product.get('category', 'unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1

        # Check required fields
        for field in required_fields:
            if field not in product:
                errors.append(f"[{pid}] Missing required field: '{field}'")

        # Check numeric constraints
        if product.get('price', 0) <= 0:
            errors.append(f"[{pid}] Invalid price: {product.get('price')} (must be > 0)")
        if not (0 <= product.get('rating', -1) <= 5):
            errors.append(f"[{pid}] Invalid rating: {product.get('rating')} (must be between 0 and 5)")
        if product.get('stock', -1) < 0:
            errors.append(f"[{pid}] Invalid stock: {product.get('stock')} (must be >= 0)")

        # Check enums
        for field, allowed_values in enums.items():
            if field in product and product[field] not in allowed_values:
                errors.append(f"[{pid}] Invalid {field}: '{product[field]}' (must be one of {allowed_values})")

        # Check non-empty string fields
        for key in ['name', 'brand', 'material', 'occasion', 'description', 'image', 'thumbnail']:
            if key in product and (not isinstance(product[key], str) or len(product[key].strip()) == 0):
                errors.append(f"[{pid}] Field '{key}' must be non-empty string")

        # Check array fields
        for key in ['sizes', 'colors', 'tags']:
            if key in product and (not isinstance(product[key], list) or len(product[key]) == 0):
                errors.append(f"[{pid}] Field '{key}' must be a non-empty list")

    if errors:
        print("Schema Validation: FAIL")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("Schema Validation: PASS\n")

    # 3. Category Statistics
    print("Category Statistics\n")
    for cat, count in category_counts.items():
        print(f"{cat} : {count}")
    print()

    print("SUCCESS")


if __name__ == '__main__':
    validate_product_data()
