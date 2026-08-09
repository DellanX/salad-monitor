"""Windows sidecar agent that pushes host metrics into docker-hosted monitor."""

import os
import time
from datetime import datetime, timezone

import requests

from src import state as state_module
from src.config import debug, VERSION
from src.processes import update_all_processes

try:
    from src.hardware import update_all_hardware
except ImportError:  # pragma: no cover - optional dependency path
    update_all_hardware = None

try:
    from src.network import update_all_network
except ImportError:  # pragma: no cover - optional dependency path
    update_all_network = None

SIDECAR_VERSION = VERSION

SCHEMA_VERSION = "1"
TARGET_SCHEME = os.environ.get("SIDECAR_TARGET_SCHEME", "http")
TARGET_HOST = os.environ.get("SIDECAR_TARGET_HOST", "127.0.0.1")
TARGET_PORT = os.environ.get("SIDECAR_TARGET_PORT", "8000")
TARGET_PATH = os.environ.get("SIDECAR_TARGET_PATH", "/api/v1/sidecar/report")
TARGET_URL = os.environ.get(
    "SIDECAR_TARGET_URL",
    f"{TARGET_SCHEME}://{TARGET_HOST}:{TARGET_PORT}{TARGET_PATH}",
)
AUTH_TOKEN = os.environ.get("SIDECAR_AUTH_TOKEN")
PUSH_INTERVAL_SECONDS = int(os.environ.get("SIDECAR_PUSH_INTERVAL_SECONDS", "5"))
HOST_ID = os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "unknown-host"


def _build_payload() -> dict[str, object]:
    return {
        "sidecar_version": SIDECAR_VERSION,
        "schema_version": SCHEMA_VERSION,
        "host_id": HOST_ID,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "state": {
            "salad_version": state_module.state.get("salad_version"),
            "salad_uptime_seconds": state_module.state.get("salad_uptime_seconds"),
            "salad_bowl_version": state_module.state.get("salad_bowl_version"),
            "salad_bowl_uptime_seconds": state_module.state.get("salad_bowl_uptime_seconds"),
            "miner_active": state_module.state.get("miner_active"),
            "miner_name": state_module.state.get("miner_name"),
            "cpu_name": state_module.state.get("cpu_name"),
            "cpu_load_pct": state_module.state.get("cpu_load_pct"),
            "ram_used_gb": state_module.state.get("ram_used_gb"),
            "ram_total_gb": state_module.state.get("ram_total_gb"),
            "ram_load_pct": state_module.state.get("ram_load_pct"),
            "gpu_name": state_module.state.get("gpu_name"),
            "gpu_utilization_pct": state_module.state.get("gpu_utilization_pct"),
            "gpu_power_watts": state_module.state.get("gpu_power_watts"),
            "gpu_temperature_c": state_module.state.get("gpu_temperature_c"),
            "disk_type": state_module.state.get("disk_type"),
            "disk_size_gb": state_module.state.get("disk_size_gb"),
            "disk_utilization_pct": state_module.state.get("disk_utilization_pct"),
            "disk_read_mbps": state_module.state.get("disk_read_mbps"),
            "disk_write_mbps": state_module.state.get("disk_write_mbps"),
            "wsl_status": state_module.state.get("wsl_status"),
            "wsl_ram_mb": state_module.state.get("wsl_ram_mb"),
            "wsl_disk_size_gb": state_module.state.get("wsl_disk_size_gb"),
            "vnet_rx_kbps": state_module.state.get("vnet_rx_kbps"),
            "vnet_tx_kbps": state_module.state.get("vnet_tx_kbps"),
            "vnet_total_rx_gb": state_module.state.get("vnet_total_rx_gb"),
            "vnet_total_tx_gb": state_module.state.get("vnet_total_tx_gb"),
            "sgs_rx_kbps": state_module.state.get("sgs_rx_kbps"),
            "sgs_tx_kbps": state_module.state.get("sgs_tx_kbps"),
            "sgs_total_rx_mb": state_module.state.get("sgs_total_rx_mb"),
            "sgs_total_tx_mb": state_module.state.get("sgs_total_tx_mb"),
            "sgs_ram_mb": state_module.state.get("sgs_ram_mb"),
        },
    }


def run_sidecar() -> None:
    """Run continuous collection and push loop."""
    if not AUTH_TOKEN:
        raise ValueError("SIDECAR_AUTH_TOKEN must be set for sidecar mode.")

    while True:
        update_all_processes()
        if update_all_hardware:
            update_all_hardware()
        if update_all_network:
            update_all_network()

        payload = _build_payload()
        try:
            response = requests.post(
                TARGET_URL,
                json=payload,
                headers={"X-Sidecar-Token": AUTH_TOKEN},
                timeout=10,
            )
            response.raise_for_status()
            debug(f"Sidecar payload sent to {TARGET_URL}")
        except requests.RequestException as exc:
            debug(f"Sidecar push failed: {exc}")

        time.sleep(PUSH_INTERVAL_SECONDS)
