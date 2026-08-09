"""Main monitoring loop for Salad logs."""

import time

from src.config import (
    debug, resolve_log_dir,
    ENABLE_HARDWARE_MONITORING,
    ENABLE_NETWORK_MONITORING,
    ENABLE_PROCESS_MONITORING,
    ENABLE_GPU_DEMAND_API,
    COLLECTOR_MODE,
)
from src.log_watcher import get_latest_log_file, tail_file
from src.log_parser import parse_line
from src import state as state_module
from src.sidecar import get_sidecar_status

# Import monitoring modules
HARDWARE_AVAILABLE = False
NETWORK_AVAILABLE = False
PROCESSES_AVAILABLE = False
GPU_DEMAND_AVAILABLE = False

if ENABLE_HARDWARE_MONITORING:
    try:
        from src.hardware import update_all_hardware
        HARDWARE_AVAILABLE = True
    except ImportError:
        debug("Hardware monitoring not available (psutil missing)")

if ENABLE_NETWORK_MONITORING:
    try:
        from src.network import update_all_network
        NETWORK_AVAILABLE = True
    except ImportError:
        debug("Network monitoring not available (psutil missing)")

if ENABLE_PROCESS_MONITORING:
    try:
        from src.processes import update_all_processes
        PROCESSES_AVAILABLE = True
    except ImportError:
        debug("Process monitoring not available (psutil missing)")

if ENABLE_GPU_DEMAND_API:
    try:
        from src.gpu_demand import fetch_gpu_demand_data_sync
        GPU_DEMAND_AVAILABLE = True
    except ImportError:
        debug("GPU demand API not available (requests missing)")


def monitor_logs() -> None:
    """Main monitoring loop - watches for new log files and parses them."""
    last_file = None
    log_dir = resolve_log_dir()
    debug(f"Monitor thread watching directory: {log_dir}")
    debug(f"Features enabled - HW:{HARDWARE_AVAILABLE} NET:{NETWORK_AVAILABLE} PROC:{PROCESSES_AVAILABLE} GPU_API:{GPU_DEMAND_AVAILABLE}")
    
    loop_counter = 0
    state_module.set_collector_mode(COLLECTOR_MODE)

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
        
        # Update hardware and system metrics every 2 iterations (every ~2 seconds)
        if loop_counter % 2 == 0:
            if COLLECTOR_MODE == "sidecar_push":
                sidecar_status = get_sidecar_status()
                if sidecar_status["stale"]:
                    state_module.set_last_warning(
                        "Sidecar data is stale or missing; waiting for sidecar payload."
                    )
                loop_counter += 1
                time.sleep(1)
                continue

            if HARDWARE_AVAILABLE:
                try:
                    update_all_hardware()
                except Exception as e:
                    debug(f"Error in hardware monitoring: {e}")
            
            if NETWORK_AVAILABLE:
                try:
                    update_all_network()
                except Exception as e:
                    debug(f"Error in network monitoring: {e}")
            
            if PROCESSES_AVAILABLE:
                try:
                    update_all_processes()
                except Exception as e:
                    debug(f"Error in process monitoring: {e}")
            
            # Update GPU demand data (cached for 5 minutes internally)
            if GPU_DEMAND_AVAILABLE:
                try:
                    fetch_gpu_demand_data_sync()
                except Exception as e:
                    debug(f"Error fetching GPU demand: {e}")
        
        loop_counter += 1
        time.sleep(1)
