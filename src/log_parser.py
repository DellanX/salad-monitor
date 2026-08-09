"""Log line parsing logic for Salad events."""

import re
from datetime import datetime
from collections import deque
from typing import Optional

from src.config import debug
from src import state as state_module


# Track download progress metrics
_download_speed_history: deque = deque(maxlen=10)
_initial_percent_tracker: float = -1
_initial_mb_tracker: float = 0
_last_estimated_mb: float = 0


def _extract_timestamp(line: str) -> Optional[datetime]:
    """Extract timestamp from log line."""
    match = re.match(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", line)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    return None


def parse_line(line: str) -> None:
    """Parse a log line and update state based on detected events."""
    global _download_speed_history, _initial_percent_tracker, _initial_mb_tracker, _last_estimated_mb
    
    lower = line.lower()
    debug(f"Parsing line: {line.strip()}")
    
    timestamp = _extract_timestamp(line)

    # ========== Legacy parsing (keep for backward compatibility) ==========
    
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

    # ========== Enhanced parsing for new features ==========
    
    # Parse matrix status: "Received desired state from matrix - X workloads"
    match_matrix = re.search(r"Received desired state from matrix - (\d+) workloads", line)
    if match_matrix:
        workload_count = int(match_matrix.group(1))
        state_module.set_matrix_status("matrix_received", workload_count)
        debug(f"MATRIX: {workload_count} workloads")
    
    # Parse wallet information: "Wallet: Current(...), Predicted(...)"
    match_wallet = re.search(r"Wallet: Current\((.*?)\), Predicted\((.*?)\)", line)
    if match_wallet:
        balance = match_wallet.group(1)
        projected = match_wallet.group(2)
        state_module.set_wallet_info(balance, projected)
        debug(f"WALLET: balance={balance}, projected={projected}")
    
    # Parse job ID: "salad.com/sce/[uuid]"
    match_job = re.search(r"salad\.com/sce/([a-f0-9\-]+)", line)
    if match_job:
        job_id = match_job.group(1)
        current_job_id = state_module.state.get("job_id")
        if job_id != current_job_id:
            state_module.set_job_info(job_id, timestamp)
            state_module.set_container_status("Starting...")
            state_module.set_matrix_status("Initializing new job...", 1)
            # Reset download progress tracking
            global _initial_percent_tracker, _initial_mb_tracker, _last_estimated_mb
            _initial_percent_tracker = -1
            _initial_mb_tracker = 0
            _last_estimated_mb = 0
            state_module.state["download_total_mb"] = 0.0
            state_module.state["is_downloading"] = False
            state_module.state["download_progress_pct"] = None
            debug(f"JOB: new job_id={job_id}")
    
    # Parse layer progress: "Pull progress event: ...@sha256:[hash] progress"
    match_layer = re.search(r"Pull progress event: .*?@sha256:([a-f0-9]{8})[a-f0-9]*\s([0-9.]+)", line)
    if match_layer:
        active_layer = match_layer.group(1)
        layer_progress = float(match_layer.group(2).replace(",", "."))
        layer_progress = round(layer_progress * 100, 1)
        state_module.state["download_active_layer"] = active_layer
        state_module.state["download_layer_progress"] = layer_progress
        debug(f"LAYER: {active_layer} @ {layer_progress}%")
    
    # Parse global download progress: "Progress(0.xx)" or "Progress(1.0)"
    match_progress = re.search(r"Progress\((0[,.]\d+|1[,.]0+)\)", line)
    if match_progress:
        progress_str = match_progress.group(1).replace(",", ".")
        progress_pct = round(float(progress_str) * 100, 1)
        
        # Track total downloaded MB (would need to be tracked from network stats)
        total_mb = state_module.state.get("download_total_mb", 0.0)
        
        # Initialize tracking on first progress event
        if _initial_percent_tracker == -1 or progress_pct < state_module.state.get("download_progress_pct", 0):
            _initial_percent_tracker = progress_pct
            _initial_mb_tracker = total_mb
        
        # Calculate estimated total size if we have enough delta
        delta_pct = progress_pct - _initial_percent_tracker
        delta_mb = total_mb - _initial_mb_tracker
        
        if delta_pct >= 1.0 and delta_mb >= 10:
            phase_estimate = (delta_mb * 100.0) / delta_pct
            _last_estimated_mb = _initial_mb_tracker + phase_estimate
        
        # Calculate absolute downloaded MB
        absolute_downloaded_mb = total_mb
        if _last_estimated_mb > 0:
            calculated_download = (_last_estimated_mb * progress_pct) / 100.0
            absolute_downloaded_mb = max(calculated_download, total_mb)
        
        # Calculate ETA
        eta_seconds = None
        if _last_estimated_mb > 0:
            remaining_mb = _last_estimated_mb - absolute_downloaded_mb
            if remaining_mb > 0:
                avg_speed_kbps = sum(_download_speed_history) / len(_download_speed_history) if _download_speed_history else 0
                if avg_speed_kbps > 0:
                    speed_mbps = avg_speed_kbps / 1024.0
                    if speed_mbps > 0.1:
                        eta_seconds = remaining_mb / speed_mbps
                        if eta_seconds > 86400:  # Cap at 24 hours
                            eta_seconds = 86400
        
        speed_kbps = state_module.state.get("vnet_rx_kbps", 0.0)
        
        state_module.set_download_progress(
            progress_pct=progress_pct,
            total_mb=absolute_downloaded_mb,
            estimated_mb=_last_estimated_mb if _last_estimated_mb > 0 else None,
            eta_seconds=eta_seconds,
            speed_kbps=speed_kbps
        )
        
        status_str = f"Global: {progress_pct}%"
        if state_module.state.get("download_active_layer"):
            status_str += f" | Layer: {state_module.state['download_active_layer']}"
        state_module.set_container_status(status_str)
        debug(f"DOWNLOAD: {progress_pct}% (estimated: {_last_estimated_mb:.0f} MB)")
    
    # Parse container running status
    if "Running(Ready" in line or "already running" in line or "already installed" in line:
        state_module.set_container_status("Running (Stable)")
        state_module.state["is_downloading"] = False
        state_module.state["download_progress_pct"] = None
        debug("CONTAINER: Running")
    
    # Parse container stopped/failed status
    if "Killed" in line or "Stopped" in line or "failed" in line:
        progress_pct = state_module.state.get("download_progress_pct")
        if progress_pct and 0 < progress_pct < 100:
            state_module.set_container_status(f"Network Hiccup / Retrying... (Frozen at {progress_pct}%)")
        else:
            state_module.set_container_status("Stopped / Waiting")
            state_module.state["is_downloading"] = False
            state_module.state["download_progress_pct"] = None
        debug("CONTAINER: Stopped/Failed")
    
    # Parse bandwidth node: "Bandwidth-[alphanumeric]"
    match_bandwidth = re.search(r"(Bandwidth-[a-zA-Z0-9\-]+)", line)
    if match_bandwidth:
        node_name = match_bandwidth.group(1)
        state_module.set_bandwidth_node(node_name, active=True)
        debug(f"BANDWIDTH: node={node_name}")
    
    # Detect bandwidth stopping
    if "Stopping workload" in line and "Bandwidth" in line:
        state_module.set_bandwidth_node("Waiting for node...", active=False)
        debug("BANDWIDTH: stopped")
    
    # Parse WSL disk size: "DistroSize = [bytes]"
    match_disk = re.search(r"DistroSize\s*=\s*([0-9.]+)", line)
    if match_disk:
        bytes_value = float(match_disk.group(1))
        size_gb = bytes_value / 1073741824.0  # Convert to GB
        state_module.set_wsl_disk_size(round(size_gb, 2))
        debug(f"WSL_DISK: {size_gb:.2f} GB")
    
    # Parse warnings and errors: [WRN], [ERR], or "failed"
    if "[WRN]" in line or "[ERR]" in line or "failed" in lower:
        # Extract message after the log level
        match_error = re.search(r"\]\s+(.*)", line)
        if match_error:
            message = match_error.group(1)
            # Truncate if too long
            if len(message) > 85:
                message = message[:82] + "..."
            state_module.set_last_warning(message)
            debug(f"WARNING: {message}")

