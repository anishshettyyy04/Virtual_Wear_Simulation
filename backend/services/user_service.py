"""
User Service Layer
Virtual Wear Simulation — Phase 1.4 REST API
"""

import json
import os


class UserService:

    def __init__(self, users_file=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.users_file = users_file or os.path.join(base_dir, 'data', 'user_preferences.json')
        self._users = None

    def _load_users(self):
        if self._users is None:
            if not os.path.exists(self.users_file):
                raise FileNotFoundError(f"User preferences dataset missing at '{self.users_file}'")
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_list = json.load(f)
                self._users = {u['userId']: u for u in users_list}
        return self._users

    def get_user_by_id(self, user_id):
        users = self._load_users()
        return users.get(user_id)
