"""Configuration and settings for the Salad Monitor."""

import os

DEFAULT_LOG_DIR = "/logs"

# Version compiled at build time
try:
    from version import VERSION
except Exception:
    VERSION = "unknown"

# Debug mode (compile-time or env override)
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"


def debug(msg: str) -> None:
    """Print debug message if DEBUG mode is enabled."""
    if DEBUG:
        print(f"[DEBUG] {msg}")


def resolve_log_dir() -> str:
    """Resolve the log directory from environment or default."""
    log_dir = os.environ.get("LOG_DIR", DEFAULT_LOG_DIR)
    debug(f"Resolved log_dir = {log_dir}")
    return log_dir
