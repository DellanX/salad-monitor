"""Global state management for the Salad Monitor."""

from typing import TypedDict, Optional


class MonitorState(TypedDict):
    salad_pending: bool
    salad_active: bool
    gpu_reserved: bool
    last_event: Optional[str]
    current_logfile: Optional[str]


state: MonitorState = {
    "salad_pending": False,
    "salad_active": False,
    "gpu_reserved": False,
    "last_event": None,
    "current_logfile": None,
}


def reset_state() -> None:
    """Reset state to idle values."""
    state["salad_active"] = False
    state["gpu_reserved"] = False
    state["salad_pending"] = False
    state["last_event"] = "idle"


def set_pending() -> None:
    """Mark workload as pending."""
    state["salad_pending"] = True
    state["last_event"] = "pending"


def set_gpu_reserved() -> None:
    """Mark GPU as reserved."""
    state["gpu_reserved"] = True
    state["last_event"] = "gpu_reserved"


def set_active() -> None:
    """Mark workload as active."""
    state["salad_active"] = True
    state["last_event"] = "active"


def set_current_logfile(path: str) -> None:
    """Update the current logfile being monitored."""
    state["current_logfile"] = path
