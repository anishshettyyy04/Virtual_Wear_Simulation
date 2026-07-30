import logging
import sys

from app.config.settings import settings


class Formatter(logging.Formatter):
    """Custom logger formatter emitting timestamp | LOG_LEVEL | module | message."""

    def format(self, record: logging.LogRecord) -> str:
        record.asctime = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        prefix = f"{record.asctime} | {record.levelname:<7} | {record.name}"
        return f"{prefix} | {record.getMessage()}"


def setup_logger(name: str = "app") -> logging.Logger:
    """Configures and returns a thread-safe logger without duplicating handlers."""
    logger = logging.getLogger(name)

    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    level = log_level_map.get(settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(Formatter())
        logger.addHandler(console_handler)

    logger.propagate = False
    return logger


logger = setup_logger("app.main")
