"""
Recommendation History Manager Subsystem
Virtual Wear Simulation — Phase 1.3 Optimization
"""

from datetime import datetime, timedelta, timezone
import json
import os


class RecommendationHistoryManager:
    """
    Manages recommendation history persistence, tracking recommendation timestamps,
    preventing repetitive suggestions, and purging stale history entries.
    """

    def __init__(self, storage_file=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.storage_file = storage_file or os.path.join(base_dir, 'data', 'recommendation_history.json')
        self._history = self._load()

    def _load(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self._history, f, indent=2)
        except Exception:
            pass

    def save_history(self, user_id, product_ids):
        """
        Saves recommended product IDs for user_id with current UTC timestamp.
        """
        if not user_id or not product_ids:
            return

        if user_id not in self._history:
            self._history[user_id] = []

        now_str = datetime.now(timezone.utc).isoformat()
        for pid in product_ids:
            self._history[user_id].append({
                "productId": pid,
                "timestamp": now_str
            })

        self._save()

    def load_history(self, user_id):
        """
        Loads list of recommended product IDs for user_id.
        """
        user_entries = self._history.get(user_id, [])
        return [entry["productId"] for entry in user_entries if isinstance(entry, dict) and "productId" in entry]

    def clear_history(self, user_id):
        """
        Clears history entries for user_id.
        """
        if user_id in self._history:
            del self._history[user_id]
            self._save()
            return True
        return False

    def remove_old_entries(self, max_age_days=30):
        """
        Purges recommendation entries older than max_age_days.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        purged_count = 0

        for uid in list(self._history.keys()):
            new_entries = []
            for entry in self._history[uid]:
                try:
                    ts_str = entry.get("timestamp")
                    entry_dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if entry_dt >= cutoff:
                        new_entries.append(entry)
                    else:
                        purged_count += 1
                except Exception:
                    new_entries.append(entry)
            self._history[uid] = new_entries

        self._save()
        return purged_count


_history_manager = None


def get_history_manager():
    global _history_manager
    if _history_manager is None:
        _history_manager = RecommendationHistoryManager()
    return _history_manager
