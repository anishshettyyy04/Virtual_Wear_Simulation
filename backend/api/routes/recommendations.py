"""
Recommendations Router Wrapper (Backward Compatibility)
Virtual Wear Simulation — Phase 1.4 Production
"""

try:
    from api.v1.recommendations import router
except ImportError:
    from backend.api.v1.recommendations import router

__all__ = ['router']
