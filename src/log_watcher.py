"""Log file watching and tailing utilities."""

import glob
import os
import time
from typing import Generator, Optional

from src.config import debug, resolve_log_dir


def get_latest_log_file() -> Optional[str]:
    """Get the most recent log file from the log directory."""
    log_dir = resolve_log_dir()
    files = sorted(glob.glob(os.path.join(log_dir, "log-*.txt")))
    debug(f"Files found in {log_dir}: {files}")
    return files[-1] if files else None


def get_all_log_files() -> list[str]:
    """Get all log files from the log directory."""
    log_dir = resolve_log_dir()
    return sorted(glob.glob(os.path.join(log_dir, "log-*.txt")))


def tail_file(path: str) -> Generator[str, None, None]:
    """Tail a file and yield new lines as they appear."""
    debug(f"Starting to tail file: {path}")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)  # Seek to end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            debug(f"TAIL: {line.strip()}")
            yield line


def read_logfile_lines(path: str, lines: Optional[int] = None) -> list[str]:
    """Read lines from a logfile, optionally limited to last N lines."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.readlines()
        if lines is not None:
            return content[-lines:]
        return content
