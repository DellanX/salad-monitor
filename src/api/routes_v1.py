"""FastAPI v1 route definitions with enhanced monitoring capabilities."""

import os
from fastapi import APIRouter
from typing import Dict, Any

from src.config import DEBUG, VERSION, resolve_log_dir
from src.state import state, update_job_uptime
from src.log_watcher import get_all_log_files, read_logfile_lines

router = APIRouter(prefix="/api/v1", tags=["v1"])


def _serialize_state(state_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize state dict, converting datetime objects to ISO strings."""
    from datetime import datetime
    
    result = {}
    for key, value in state_dict.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


@router.get("/health")
def health_v1():
    """Get comprehensive health and status information (v1)."""
    # Update job uptime before returning
    update_job_uptime()
    
    return {
        "monitor_running": True,
        "current_logfile": state.get("current_logfile"),
        "log_dir": resolve_log_dir(),
        "version": VERSION,
        "debug": DEBUG,
        "state": _serialize_state(state),
    }


@router.get("/wallet")
def wallet_info():
    """Get wallet balance and projected earnings."""
    return {
        "balance": state.get("wallet_balance"),
        "projected": state.get("wallet_projected"),
        "last_update": state.get("wallet_last_update").isoformat() if state.get("wallet_last_update") else None,
    }


@router.get("/job")
def job_info():
    """Get current job details and uptime."""
    update_job_uptime()
    
    return {
        "job_id": state.get("job_id"),
        "start_time": state.get("job_start_time").isoformat() if state.get("job_start_time") else None,
        "uptime_seconds": state.get("job_uptime_seconds"),
        "container_status": state.get("container_status"),
        "matrix_status": state.get("matrix_status"),
    }


@router.get("/download")
def download_progress():
    """Get container download progress and status."""
    return {
        "is_downloading": state.get("is_downloading", False),
        "progress_pct": state.get("download_progress_pct"),
        "active_layer": state.get("download_active_layer"),
        "layer_progress": state.get("download_layer_progress"),
        "speed_kbps": state.get("download_speed_kbps"),
        "total_mb": state.get("download_total_mb"),
        "estimated_mb": state.get("download_estimated_mb"),
        "eta_seconds": state.get("download_eta_seconds"),
    }


@router.get("/hardware")
def hardware_metrics():
    """Get hardware metrics (CPU, RAM, GPU, Disk)."""
    return {
        "cpu": {
            "name": state.get("cpu_name"),
            "load_pct": state.get("cpu_load_pct"),
        },
        "ram": {
            "used_gb": state.get("ram_used_gb"),
            "total_gb": state.get("ram_total_gb"),
            "load_pct": state.get("ram_load_pct"),
        },
        "gpu": {
            "name": state.get("gpu_name"),
            "utilization_pct": state.get("gpu_utilization_pct"),
            "power_watts": state.get("gpu_power_watts"),
            "temperature_c": state.get("gpu_temperature_c"),
        },
        "disk": {
            "type": state.get("disk_type"),
            "size_gb": state.get("disk_size_gb"),
            "utilization_pct": state.get("disk_utilization_pct"),
            "read_mbps": state.get("disk_read_mbps"),
            "write_mbps": state.get("disk_write_mbps"),
        },
    }


@router.get("/network")
def network_stats():
    """Get network statistics (WSL and SGS)."""
    return {
        "wsl": {
            "rx_kbps": state.get("vnet_rx_kbps"),
            "tx_kbps": state.get("vnet_tx_kbps"),
            "total_rx_gb": state.get("vnet_total_rx_gb"),
            "total_tx_gb": state.get("vnet_total_tx_gb"),
        },
        "sgs": {
            "rx_kbps": state.get("sgs_rx_kbps"),
            "tx_kbps": state.get("sgs_tx_kbps"),
            "total_rx_mb": state.get("sgs_total_rx_mb"),
            "total_tx_mb": state.get("sgs_total_tx_mb"),
            "ram_mb": state.get("sgs_ram_mb"),
        },
        "bandwidth": {
            "active": state.get("bandwidth_active", False),
            "node_name": state.get("bandwidth_node_name"),
        },
    }


@router.get("/wsl")
def wsl_status():
    """Get WSL status and resource usage."""
    return {
        "status": state.get("wsl_status"),
        "ram_mb": state.get("wsl_ram_mb"),
        "disk_size_gb": state.get("wsl_disk_size_gb"),
    }


@router.get("/gpu-demand")
def gpu_demand():
    """Get GPU demand data from Salad API."""
    return {
        "tier": state.get("gpu_demand_tier"),
        "utilization_pct": state.get("gpu_demand_utilization_pct"),
        "earning_avg_24h": state.get("gpu_earning_avg_24h"),
        "earning_max_24h": state.get("gpu_earning_max_24h"),
        "recommended_ram_gb": state.get("gpu_recommended_ram_gb"),
        "last_update": state.get("gpu_demand_last_update").isoformat() if state.get("gpu_demand_last_update") else None,
    }


@router.get("/processes")
def process_info():
    """Get Salad process information and miner detection."""
    return {
        "salad": {
            "version": state.get("salad_version"),
            "uptime_seconds": state.get("salad_uptime_seconds"),
        },
        "salad_bowl": {
            "version": state.get("salad_bowl_version"),
            "uptime_seconds": state.get("salad_bowl_uptime_seconds"),
        },
        "miner": {
            "active": state.get("miner_active", False),
            "name": state.get("miner_name"),
        },
    }


@router.get("/errors")
def error_info():
    """Get last warning/error information."""
    return {
        "last_warning": state.get("last_warning"),
        "last_warning_time": state.get("last_warning_time").isoformat() if state.get("last_warning_time") else None,
    }


@router.get("/current-logfile")
def current_logfile():
    """Get the path of the currently monitored logfile."""
    return {"current_logfile": state.get("current_logfile")}


@router.get("/current-logfile-contents")
def current_logfile_contents(lines: int | None = None):
    """Get contents of the current logfile, optionally limited to last N lines."""
    logfile = state.get("current_logfile")
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
    logfile = state.get("current_logfile")
    if not logfile or not os.path.exists(logfile):
        return {"error": "No logfile available"}

    raw = read_logfile_lines(logfile, lines)
    return {"logfile": logfile, "lines": raw}


@router.get("/version")
def version():
    """Get the application version."""
    return {"version": VERSION}
