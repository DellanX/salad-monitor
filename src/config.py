"""Configuration and settings for the Salad Monitor."""

import os

DEFAULT_LOG_DIR = "/logs"

# Version compiled at build time
try:
    from version import VERSION
except Exception:
    VERSION = "0.2.0"

# Debug mode (compile-time or env override)
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Feature toggles
ENABLE_HARDWARE_MONITORING = os.environ.get("ENABLE_HARDWARE_MONITORING", "true").lower() == "true"
ENABLE_GPU_DEMAND_API = os.environ.get("ENABLE_GPU_DEMAND_API", "true").lower() == "true"
ENABLE_NETWORK_MONITORING = os.environ.get("ENABLE_NETWORK_MONITORING", "true").lower() == "true"
ENABLE_PROCESS_MONITORING = os.environ.get("ENABLE_PROCESS_MONITORING", "true").lower() == "true"

# GPU demand API cache duration (in minutes)
GPU_DEMAND_CACHE_MINUTES = int(os.environ.get("GPU_DEMAND_CACHE_MINUTES", "5"))


def debug(msg: str) -> None:
    """Print debug message if DEBUG mode is enabled."""
    if DEBUG:
        print(f"[DEBUG] {msg}")


def resolve_log_dir() -> str:
    """Resolve the log directory from environment or default."""
    log_dir = os.environ.get("LOG_DIR", DEFAULT_LOG_DIR)
    debug(f"Resolved log_dir = {log_dir}")
    return log_dir

