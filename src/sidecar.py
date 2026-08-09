"""Sidecar payload handling and compatibility checks."""

from datetime import datetime, timezone
from typing import Any

from src import state as state_module
from src.config import MINIMUM_SIDECAR_VERSION, SIDECAR_STALE_SECONDS

SIDE_CAR_MUTABLE_STATE_KEYS = {
    "salad_version",
    "salad_uptime_seconds",
    "salad_bowl_version",
    "salad_bowl_uptime_seconds",
    "miner_active",
    "miner_name",
    "cpu_name",
    "cpu_load_pct",
    "ram_used_gb",
    "ram_total_gb",
    "ram_load_pct",
    "gpu_name",
    "gpu_utilization_pct",
    "gpu_power_watts",
    "gpu_temperature_c",
    "disk_type",
    "disk_size_gb",
    "disk_utilization_pct",
    "disk_read_mbps",
    "disk_write_mbps",
    "wsl_status",
    "wsl_ram_mb",
    "wsl_disk_size_gb",
    "vnet_rx_kbps",
    "vnet_tx_kbps",
    "vnet_total_rx_gb",
    "vnet_total_tx_gb",
    "sgs_rx_kbps",
    "sgs_tx_kbps",
    "sgs_total_rx_mb",
    "sgs_total_tx_mb",
    "sgs_ram_mb",
}


def _parse_version(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for section in version.split("."):
        digits = "".join(char for char in section if char.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _to_utc_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        normalized = raw.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def is_sidecar_update_required(sidecar_version: str | None) -> bool:
    """Return True when sidecar version is below configured minimum."""
    if not sidecar_version:
        return False
    return _parse_version(sidecar_version) < _parse_version(MINIMUM_SIDECAR_VERSION)


def apply_sidecar_payload(payload: dict[str, Any]) -> None:
    """Apply validated sidecar payload data into shared state."""
    state_data = payload.get("state", {})
    if isinstance(state_data, dict):
        for key, value in state_data.items():
            if key in SIDE_CAR_MUTABLE_STATE_KEYS:
                state_module.state[key] = value

    sidecar_version = payload.get("sidecar_version")
    schema_version = payload.get("schema_version")
    host_id = payload.get("host_id")
    collected_at = _to_utc_datetime(payload.get("collected_at"))

    state_module.state["sidecar_version"] = sidecar_version
    state_module.state["sidecar_schema_version"] = schema_version
    state_module.state["sidecar_host_id"] = host_id
    state_module.state["sidecar_last_seen"] = datetime.now(timezone.utc)
    state_module.state["sidecar_last_payload_time"] = collected_at
    state_module.state["sidecar_update_required"] = is_sidecar_update_required(sidecar_version)
    state_module.set_process_data_source("sidecar")


def get_sidecar_status(now: datetime | None = None) -> dict[str, Any]:
    """Return sidecar status metadata for API responses and health checks."""
    current_time = now or datetime.now(timezone.utc)
    last_seen = state_module.state.get("sidecar_last_seen")
    stale = True
    seconds_since_last_seen = None

    if isinstance(last_seen, datetime):
        aware_last_seen = last_seen if last_seen.tzinfo else last_seen.replace(tzinfo=timezone.utc)
        delta = (current_time - aware_last_seen).total_seconds()
        seconds_since_last_seen = max(0.0, delta)
        stale = seconds_since_last_seen > SIDECAR_STALE_SECONDS

    return {
        "configured_stale_seconds": SIDECAR_STALE_SECONDS,
        "last_seen": last_seen.isoformat() if isinstance(last_seen, datetime) else None,
        "seconds_since_last_seen": seconds_since_last_seen,
        "stale": stale,
        "sidecar_version": state_module.state.get("sidecar_version"),
        "schema_version": state_module.state.get("sidecar_schema_version"),
        "host_id": state_module.state.get("sidecar_host_id"),
        "update_required": state_module.state.get("sidecar_update_required", False),
        "minimum_supported_version": MINIMUM_SIDECAR_VERSION,
    }
