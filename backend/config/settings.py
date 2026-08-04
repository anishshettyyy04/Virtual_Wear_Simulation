"""
Centralized Application Settings
Virtual Wear Simulation — Phase 1.4 Production
"""

import os
from typing import List


class Settings:
    """
    Centralized configuration management for environment variables and system settings.
    """

    def __init__(self):
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.API_VERSION: str = os.getenv("API_VERSION", "v1")
        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME", "AI Virtual Wear Simulation")

        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
        self.ALLOWED_ORIGINS: List[str] = [o.strip() for o in origins_str.split(",") if o.strip()]


settings = Settings()
