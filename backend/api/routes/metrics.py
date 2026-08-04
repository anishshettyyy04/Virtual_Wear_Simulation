"""
Metrics Router Wrapper (Backward Compatibility)
Virtual Wear Simulation — Phase 1.4 Production
"""

try:
    from api.v1.metrics import router
except ImportError:
    from backend.api.v1.metrics import router

__all__ = ['router']
