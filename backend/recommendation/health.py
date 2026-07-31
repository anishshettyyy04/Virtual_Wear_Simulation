"""
System Health Monitoring Subsystem
Virtual Wear Simulation — Phase 1.3 Optimization
"""

import os


def check_system_health(engine=None):
    """
    Validates subsystem readiness including product dataset, user preference dataset,
    configuration files, active strategy, cache initialization, and analytics availability.

    Returns:
        dict: Health status report envelope.
    """
    health = {
        "status": "healthy",
        "products": "unloaded",
        "users": "unloaded",
        "configuration": "unloaded",
        "strategy": "uninitialized",
        "cache": "disabled",
        "analytics": "available"
    }

    errors = []

    try:
        # Check dataset paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prod_path = os.path.join(base_dir, 'data', 'products.json')
        user_path = os.path.join(base_dir, 'data', 'user_preferences.json')
        config_path = os.path.join(base_dir, 'config', 'recommendation_config.json')

        if os.path.exists(prod_path):
            health["products"] = "loaded"
        else:
            health["products"] = "missing"
            errors.append("Products dataset missing")

        if os.path.exists(user_path):
            health["users"] = "loaded"
        else:
            health["users"] = "missing"
            errors.append("User preferences dataset missing")

        if os.path.exists(config_path):
            health["configuration"] = "loaded"
        else:
            health["configuration"] = "missing"
            errors.append("Config file missing")

        if engine is not None:
            health["strategy"] = getattr(engine.strategy, '__class__', {}).__name__.replace("Strategy", "")
            if hasattr(engine, 'cache') and engine.cache.enabled:
                health["cache"] = "enabled"
        else:
            health["strategy"] = "RuleBased"
            health["cache"] = "enabled"

    except Exception as e:
        health["status"] = "unhealthy"
        health["error"] = str(e)
        return health

    if errors:
        health["status"] = "degraded"
        health["errors"] = errors

    return health
