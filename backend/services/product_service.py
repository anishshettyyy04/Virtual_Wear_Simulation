"""
Product Service Layer
Virtual Wear Simulation — Phase 1.4 REST API
"""

json_data_cache = None


import json
import os


class ProductService:

    def __init__(self, products_file=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.products_file = products_file or os.path.join(base_dir, 'data', 'products.json')
        self._products = None

    def _load_products(self):
        if self._products is None:
            if not os.path.exists(self.products_file):
                raise FileNotFoundError(f"Products dataset missing at '{self.products_file}'")
            with open(self.products_file, 'r', encoding='utf-8') as f:
                self._products = json.load(f)
        return self._products

    def get_all_products(self, category=None, gender=None):
        products = self._load_products()
        filtered = products

        if category:
            filtered = [p for p in filtered if p.get('category') == category]

        if gender:
            filtered = [p for p in filtered if p.get('gender') == gender or p.get('gender') == 'unisex']

        return filtered

    def get_product_by_id(self, product_id):
        products = self._load_products()
        for p in products:
            if p.get('id') == product_id:
                return p
        return None
