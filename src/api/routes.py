"""FastAPI route definitions."""

import os
from fastapi import APIRouter

from src.config import DEBUG, VERSION, resolve_log_dir, get_feature_flags
from src.state import state
from src.log_watcher import get_all_log_files, read_logfile_lines

router = APIRouter()


@router.get("/gpu-status")
def gpu_status():
    """Get current GPU and workload status."""
    return state


@router.get("/current-logfile")
def current_logfile():
    """Get the path of the currently monitored logfile."""
    return {"current_logfile": state["current_logfile"]}


@router.get("/current-logfile-contents")
def current_logfile_contents(lines: int | None = None):
    """Get contents of the current logfile, optionally limited to last N lines."""
    logfile = state["current_logfile"]
    if not logfile or not os.path.exists(logfile):
        return {"error": "No logfile available"}

    content = read_logfile_lines(logfile, lines)
    return {"logfile": logfile, "lines": content}


@router.get("/logs")
def list_logs():
    """List all available log files."""
    log_dir = resolve_log_dir()
    files = get_all_log_files()
    return {"log_dir": log_dir, "files": files}


@router.get("/tail")
def tail_raw(lines: int = 50):
    """Get the last N lines of the current logfile."""
    logfile = state["current_logfile"]
    if not logfile or not os.path.exists(logfile):
        return {"error": "No logfile available"}

    raw = read_logfile_lines(logfile, lines)
    return {"logfile": logfile, "lines": raw}


@router.get("/version")
def version():
    """Get the application version."""
    return {"version": VERSION}


@router.get("/debug")
def debug_status():
    """Get debug mode status."""
    return {"debug": DEBUG}


@router.get("/health")
def health():
    """Get overall health and status information."""
    return {
        "monitor_running": True,
        "current_logfile": state["current_logfile"],
        "log_dir": resolve_log_dir(),
        "version": VERSION,
        "debug": DEBUG,
        "features": get_feature_flags(),
        "state": state,
    }
