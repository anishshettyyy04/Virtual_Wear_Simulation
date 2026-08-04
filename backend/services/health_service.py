"""
Health Monitor Service Layer
Virtual Wear Simulation — Phase 1.4 REST API
"""

try:
    from recommendation.health import check_system_health
except ImportError:
    from backend.recommendation.health import check_system_health


class HealthService:

    @staticmethod
    def get_health_status(engine=None):
        return check_system_health(engine=engine)
