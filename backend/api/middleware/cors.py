"""
CORS Middleware Configuration
Virtual Wear Simulation — Phase 1.4 REST API
"""

import os
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
    origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

    if "*" in origins or os.getenv("DEBUG", "True").lower() == "true":
        origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
