"""Configuration and settings for the Salad Monitor."""

import os
from typing import Literal

DEFAULT_LOG_DIR = "/logs"
DEFAULT_WINDOWS_LOG_DIR = r"C:\ProgramData\Salad\logs"


def _load_env_file() -> None:
    """Load KEY=VALUE pairs from CONFIG_FILE or default .env path."""
    config_file = os.environ.get("CONFIG_FILE") or ".env"
    if not os.path.exists(config_file):
        return

    with open(config_file, "r", encoding="utf-8") as file_handle:
        for raw_line in file_handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            if not key or key in os.environ:
                continue
            os.environ[key] = value.strip().strip("'").strip('"')


_load_env_file()

# Version compiled at build time
try:
    from version import VERSION
except Exception:
    VERSION = "0.2.0"

# Debug mode (compile-time or env override)
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Feature toggles
ENABLE_HARDWARE_MONITORING = os.environ.get(
    "ENABLE_HARDWARE_MONITORING", "true").lower() == "true"
ENABLE_GPU_DEMAND_API = os.environ.get(
    "ENABLE_GPU_DEMAND_API", "true").lower() == "true"
ENABLE_NETWORK_MONITORING = os.environ.get(
    "ENABLE_NETWORK_MONITORING", "true").lower() == "true"
ENABLE_PROCESS_MONITORING = os.environ.get(
    "ENABLE_PROCESS_MONITORING", "true").lower() == "true"

# Collection mode
CollectorMode = Literal["local_psutil", "sidecar_push", "volume_scan"]
COLLECTOR_MODE: CollectorMode = os.environ.get(
    "COLLECTOR_MODE", "local_psutil"
).lower()  # type: ignore[assignment]

if COLLECTOR_MODE not in {"local_psutil", "sidecar_push", "volume_scan"}:
    COLLECTOR_MODE = "local_psutil"

# Sidecar settings (docker mode)
SIDECAR_AUTH_TOKEN = os.environ.get("SIDECAR_AUTH_TOKEN")
SIDECAR_STALE_SECONDS = int(os.environ.get("SIDECAR_STALE_SECONDS", "120"))
MINIMUM_SIDECAR_VERSION = VERSION

# Volume scan settings
SALAD_VERSION_FILE = os.environ.get("SALAD_VERSION_FILE")
SALAD_BOWL_VERSION_FILE = os.environ.get("SALAD_BOWL_VERSION_FILE")

# GPU demand API cache duration (in minutes)
GPU_DEMAND_CACHE_MINUTES = int(os.environ.get("GPU_DEMAND_CACHE_MINUTES", "5"))


def get_feature_flags() -> dict[str, bool]:
    """Return current feature-toggle values for API status reporting."""
    return {
        "ENABLE_HARDWARE_MONITORING": ENABLE_HARDWARE_MONITORING,
        "ENABLE_GPU_DEMAND_API": ENABLE_GPU_DEMAND_API,
        "ENABLE_NETWORK_MONITORING": ENABLE_NETWORK_MONITORING,
        "ENABLE_PROCESS_MONITORING": ENABLE_PROCESS_MONITORING,
    }


def get_runtime_settings() -> dict[str, str | int | bool | None]:
    """Return runtime settings relevant to collection behavior."""
    return {
        "COLLECTOR_MODE": COLLECTOR_MODE,
        "SIDECAR_STALE_SECONDS": SIDECAR_STALE_SECONDS,
        "MINIMUM_SIDECAR_VERSION": MINIMUM_SIDECAR_VERSION,
        "SIDECAR_AUTH_TOKEN_CONFIGURED": bool(SIDECAR_AUTH_TOKEN),
        "SALAD_VERSION_FILE": SALAD_VERSION_FILE,
        "SALAD_BOWL_VERSION_FILE": SALAD_BOWL_VERSION_FILE,
    }


def debug(msg: str) -> None:
    """Print debug message if DEBUG mode is enabled."""
    if DEBUG:
        print(f"[DEBUG] {msg}")


def resolve_log_dir() -> str:
    """Resolve the log directory from environment or default."""
    default_log_dir = DEFAULT_WINDOWS_LOG_DIR if os.name == "nt" else DEFAULT_LOG_DIR
    log_dir = os.environ.get("LOG_DIR", default_log_dir)
    debug(f"Resolved log_dir = {log_dir}")
    return log_dir
