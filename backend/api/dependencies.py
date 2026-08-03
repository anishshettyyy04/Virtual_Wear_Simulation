"""
FastAPI Dependency Injection Providers
Virtual Wear Simulation — Phase 1.4 REST API
"""

try:
    from services.health_service import HealthService
    from services.metrics_service import MetricsService
    from services.product_service import ProductService
    from services.recommendation_service import RecommendationService
    from services.user_service import UserService
except ImportError:
    from backend.services.health_service import HealthService
    from backend.services.metrics_service import MetricsService
    from backend.services.product_service import ProductService
    from backend.services.recommendation_service import RecommendationService
    from backend.services.user_service import UserService


def get_product_service():
    return ProductService()


def get_user_service():
    return UserService()


def get_recommendation_service():
    return RecommendationService()


def get_health_service():
    return HealthService()


def get_metrics_service():
    return MetricsService()
