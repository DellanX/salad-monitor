"""Log line parsing logic for Salad events."""

from src.config import debug
from src import state as state_module


def parse_line(line: str) -> None:
    """Parse a log line and update state based on detected events."""
    lower = line.lower()
    debug(f"Parsing line: {line.strip()}")

    # Check for pending workload
    if (
        "workload received" in lower
        or "planned actions" in lower
        or "requestinstall" in lower
    ):
        state_module.set_pending()
        debug("EVENT: pending")

    # Check for GPU reservation
    if "gpu hardwarecompatibility" in lower:
        state_module.set_gpu_reserved()
        debug("EVENT: gpu_reserved")

    # Check for active workload
    if "is already running" in lower or "starting workload" in lower:
        state_module.set_active()
        debug("EVENT: active")

    # Check for workload completion
    if "workload completed" in lower or "releasing gpu" in lower:
        state_module.reset_state()
        debug("EVENT: idle")
