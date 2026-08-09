"""Global state management for the Salad Monitor."""

from typing import TypedDict, Optional
from datetime import datetime


class MonitorState(TypedDict, total=False):
    # Legacy fields (kept for backward compatibility)
    salad_pending: bool
    salad_active: bool
    gpu_reserved: bool
    last_event: Optional[str]
    current_logfile: Optional[str]
    
    # Wallet information
    wallet_balance: Optional[str]
    wallet_projected: Optional[str]
    wallet_last_update: Optional[datetime]
    
    # Job information
    job_id: Optional[str]
    job_start_time: Optional[datetime]
    job_uptime_seconds: Optional[float]
    matrix_status: Optional[str]
    container_status: Optional[str]
    
    # Download progress
    download_progress_pct: Optional[float]
    download_active_layer: Optional[str]
    download_layer_progress: Optional[float]
    download_speed_kbps: Optional[float]
    download_total_mb: Optional[float]
    download_estimated_mb: Optional[float]
    download_eta_seconds: Optional[float]
    is_downloading: bool
    
    # WSL information
    wsl_status: Optional[str]
    wsl_ram_mb: Optional[float]
    wsl_disk_size_gb: Optional[float]
    
    # Network information
    bandwidth_active: bool
    bandwidth_node_name: Optional[str]
    vnet_rx_kbps: Optional[float]
    vnet_tx_kbps: Optional[float]
    vnet_total_rx_gb: Optional[float]
    vnet_total_tx_gb: Optional[float]
    sgs_rx_kbps: Optional[float]
    sgs_tx_kbps: Optional[float]
    sgs_total_rx_mb: Optional[float]
    sgs_total_tx_mb: Optional[float]
    sgs_ram_mb: Optional[float]
    
    # Hardware metrics
    cpu_name: Optional[str]
    cpu_load_pct: Optional[float]
    ram_used_gb: Optional[float]
    ram_total_gb: Optional[float]
    ram_load_pct: Optional[float]
    gpu_name: Optional[str]
    gpu_utilization_pct: Optional[float]
    gpu_power_watts: Optional[float]
    gpu_temperature_c: Optional[float]
    disk_type: Optional[str]
    disk_size_gb: Optional[float]
    disk_utilization_pct: Optional[float]
    disk_read_mbps: Optional[float]
    disk_write_mbps: Optional[float]
    
    # GPU demand data (from Salad API)
    gpu_demand_tier: Optional[str]
    gpu_demand_utilization_pct: Optional[float]
    gpu_earning_avg_24h: Optional[float]
    gpu_earning_max_24h: Optional[float]
    gpu_recommended_ram_gb: Optional[int]
    gpu_demand_last_update: Optional[datetime]
    
    # Process information
    salad_version: Optional[str]
    salad_uptime_seconds: Optional[float]
    salad_bowl_version: Optional[str]
    salad_bowl_uptime_seconds: Optional[float]
    miner_active: bool
    miner_name: Optional[str]

    # Collection/source information
    collector_mode: str
    process_data_source: Optional[str]
    sidecar_version: Optional[str]
    sidecar_schema_version: Optional[str]
    sidecar_host_id: Optional[str]
    sidecar_last_seen: Optional[datetime]
    sidecar_last_payload_time: Optional[datetime]
    sidecar_update_required: bool
    
    # Error tracking
    last_warning: Optional[str]
    last_warning_time: Optional[datetime]


state: MonitorState = {
    # Legacy fields
    "salad_pending": False,
    "salad_active": False,
    "gpu_reserved": False,
    "last_event": None,
    "current_logfile": None,
    
    # Initialize new fields
    "wallet_balance": None,
    "wallet_projected": None,
    "wallet_last_update": None,
    "job_id": None,
    "job_start_time": None,
    "job_uptime_seconds": None,
    "matrix_status": None,
    "container_status": "Pending...",
    "download_progress_pct": None,
    "download_active_layer": None,
    "download_layer_progress": None,
    "download_speed_kbps": None,
    "download_total_mb": 0.0,
    "download_estimated_mb": None,
    "download_eta_seconds": None,
    "is_downloading": False,
    "wsl_status": None,
    "wsl_ram_mb": None,
    "wsl_disk_size_gb": None,
    "bandwidth_active": False,
    "bandwidth_node_name": None,
    "vnet_rx_kbps": None,
    "vnet_tx_kbps": None,
    "vnet_total_rx_gb": 0.0,
    "vnet_total_tx_gb": 0.0,
    "sgs_rx_kbps": None,
    "sgs_tx_kbps": None,
    "sgs_total_rx_mb": 0.0,
    "sgs_total_tx_mb": 0.0,
    "sgs_ram_mb": None,
    "cpu_name": None,
    "cpu_load_pct": None,
    "ram_used_gb": None,
    "ram_total_gb": None,
    "ram_load_pct": None,
    "gpu_name": None,
    "gpu_utilization_pct": None,
    "gpu_power_watts": None,
    "gpu_temperature_c": None,
    "disk_type": None,
    "disk_size_gb": None,
    "disk_utilization_pct": None,
    "disk_read_mbps": None,
    "disk_write_mbps": None,
    "gpu_demand_tier": None,
    "gpu_demand_utilization_pct": None,
    "gpu_earning_avg_24h": None,
    "gpu_earning_max_24h": None,
    "gpu_recommended_ram_gb": None,
    "gpu_demand_last_update": None,
    "salad_version": None,
    "salad_uptime_seconds": None,
    "salad_bowl_version": None,
    "salad_bowl_uptime_seconds": None,
    "miner_active": False,
    "miner_name": None,
    "collector_mode": "local_psutil",
    "process_data_source": None,
    "sidecar_version": None,
    "sidecar_schema_version": None,
    "sidecar_host_id": None,
    "sidecar_last_seen": None,
    "sidecar_last_payload_time": None,
    "sidecar_update_required": False,
    "last_warning": None,
    "last_warning_time": None,
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


# New state update functions for enhanced features

def set_wallet_info(balance: str, projected: str) -> None:
    """Update wallet balance and projected earnings."""
    state["wallet_balance"] = balance
    state["wallet_projected"] = projected
    state["wallet_last_update"] = datetime.now()


def set_job_info(job_id: str, start_time: Optional[datetime] = None) -> None:
    """Update current job information."""
    state["job_id"] = job_id
    if start_time:
        state["job_start_time"] = start_time
    elif not state.get("job_start_time"):
        state["job_start_time"] = datetime.now()


def update_job_uptime() -> None:
    """Calculate and update job uptime."""
    if state.get("job_start_time") and state.get("job_id"):
        uptime = (datetime.now() - state["job_start_time"]).total_seconds()
        state["job_uptime_seconds"] = uptime


def set_container_status(status: str) -> None:
    """Update container status."""
    state["container_status"] = status


def set_matrix_status(status: str, workload_count: int = 0) -> None:
    """Update matrix status."""
    if workload_count == 0:
        state["matrix_status"] = "Idle - Searching for jobs..."
        state["container_status"] = "Stopped / Waiting"
        state["is_downloading"] = False
        state["download_progress_pct"] = None
        state["job_id"] = None
    else:
        state["matrix_status"] = f"Job Acquired! ({workload_count} active workload)"


def set_download_progress(
    progress_pct: float,
    active_layer: Optional[str] = None,
    layer_progress: Optional[float] = None,
    speed_kbps: Optional[float] = None,
    total_mb: Optional[float] = None,
    estimated_mb: Optional[float] = None,
    eta_seconds: Optional[float] = None,
) -> None:
    """Update download progress information."""
    state["is_downloading"] = True
    state["download_progress_pct"] = progress_pct
    if active_layer:
        state["download_active_layer"] = active_layer
    if layer_progress is not None:
        state["download_layer_progress"] = layer_progress
    if speed_kbps is not None:
        state["download_speed_kbps"] = speed_kbps
    if total_mb is not None:
        state["download_total_mb"] = total_mb
    if estimated_mb is not None:
        state["download_estimated_mb"] = estimated_mb
    if eta_seconds is not None:
        state["download_eta_seconds"] = eta_seconds


def set_wsl_disk_size(size_gb: float) -> None:
    """Update WSL disk size."""
    state["wsl_disk_size_gb"] = size_gb


def set_bandwidth_node(node_name: str, active: bool = True) -> None:
    """Update bandwidth node information."""
    state["bandwidth_node_name"] = node_name
    state["bandwidth_active"] = active


def set_last_warning(message: str) -> None:
    """Update last warning/error message."""
    state["last_warning"] = message
    state["last_warning_time"] = datetime.now()


def set_collector_mode(mode: str) -> None:
    """Update active collector mode."""
    state["collector_mode"] = mode


def set_process_data_source(source: str) -> None:
    """Track the source for current process/version fields."""
    state["process_data_source"] = source
