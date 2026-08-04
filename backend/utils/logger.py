"""
Structured JSON Logger Utility
Virtual Wear Simulation — Phase 1.4 Production
"""

from datetime import datetime, timezone
import json
import logging
import sys


class StructuredJsonFormatter(logging.Formatter):
    """
    Custom JSON log formatter outputting structured log records for production log aggregation.
    """
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "logLevel": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Inject extra attributes if passed in extra dict
        for attr in ["requestId", "endpoint", "method", "statusCode", "latency"]:
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)

        return json.dumps(log_entry)


def get_logger(name="virtual_wear"):
    """
    Returns configured structured logger instance.
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredJsonFormatter())
    logger.addHandler(console_handler)

    return logger


logger = get_logger()


def log_structured(message, level="INFO", request_id=None, endpoint=None, method=None, status_code=None, latency=None):
    """
    Helper for logging structured events with HTTP request context attributes.
    """
    extra = {
        "requestId": request_id,
        "endpoint": endpoint,
        "method": method,
        "statusCode": status_code,
        "latency": latency
    }
    lvl = getattr(logging, level.upper(), logging.INFO)
    logger.log(lvl, message, extra=extra)
