import logging
import sys
import os
from logging.handlers import RotatingFileHandler


class ExcludeFilter(logging.Filter):
    """Filter to exclude noisy log messages"""
    def filter(self, record):
        if record.name == "httpx" and "HTTP Request:" in record.getMessage():
            return False
        if record.name == "werkzeug" and "GET /api/logs" in record.getMessage():
            return False
        return True


def configure_root_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s | [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)

    # File handler
    os.makedirs("./logs", exist_ok=True)
    file_handler = RotatingFileHandler(
        "./logs/vinted_notifications.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Add exclude filter
    exclude_filter = ExcludeFilter()
    console_handler.addFilter(exclude_filter)
    file_handler.addFilter(exclude_filter)

    # Clear existing handlers to avoid duplicates
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_logger(name):
    if not logging.getLogger().handlers:
        configure_root_logger()
    return logging.getLogger(name)
