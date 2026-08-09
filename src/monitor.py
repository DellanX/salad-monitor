"""Main monitoring loop for Salad logs."""

import time

from src.config import debug, resolve_log_dir
from src.log_watcher import get_latest_log_file, tail_file
from src.log_parser import parse_line
from src import state as state_module


def monitor_logs() -> None:
    """Main monitoring loop - watches for new log files and parses them."""
    last_file = None
    log_dir = resolve_log_dir()
    debug(f"Monitor thread watching directory: {log_dir}")

    while True:
        latest = get_latest_log_file()

        if not latest:
            debug("No log files found. Sleeping...")
            time.sleep(5)
            continue

        debug(f"Latest logfile detected: {latest}")

        if latest != last_file:
            debug(f"Switching logfile from {last_file} to {latest}")
            last_file = latest
            state_module.set_current_logfile(latest)

            for line in tail_file(latest):
                parse_line(line)
