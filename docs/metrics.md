# Canonical Metrics & Snapshot Schema (`docs/metrics.md`)

This document defines the complete metric schema for `salad-monitor` v1.0, including field names, types, units, refresh intervals, data sources per platform, and required capabilities.

---

## 1. Top-Level Snapshot Schema (`Snapshot`)

The daemon maintains an in-memory `Snapshot` struct. `GET /api/v1/snapshot` returns the full JSON representation, while SSE `/api/v1/stream` broadcasts incremental `delta` objects or full `snapshot` events.

```json
{
  "timestamp": "2026-09-01T11:00:00.000Z",
  "capabilities": {
    "log_parsing": true,
    "salad_demand_api": true,
    "gpu_nvidia": true,
    "gpu_per_process": true,
    "host_processes": true,
    "wsl_status": true,
    "windows_registry": true,
    "host_nic_vethernet": true,
    "disk_smart": true,
    "miner_detection": true
  },
  "system": { ... },
  "wallet": { ... },
  "job": { ... },
  "hardware": { ... },
  "gpu_demand": { ... },
  "wsl": { ... },
  "network": { ... },
  "process": { ... },
  "log": { ... }
}
```

---

## 2. Detailed Section Schemas

### 2.1 System Metadata (`system`)

| Field | Type | Unit | Refresh | Capability | Description |
|---|---|---|---|---|---|
| `os_name` | `string` | — | Startup | None | e.g. `"Windows"`, `"Linux"` |
| `os_version` | `string` | — | Startup | None | e.g. `"Windows 11 Build 22631"`, `"Linux 6.6.0"` |
| `daemon_version` | `string` | — | Startup | None | `salad-monitor` version string |
| `uptime_seconds` | `u64` | seconds | 1s | None | OS uptime |
| `daemon_uptime_seconds` | `u64` | seconds | 1s | None | Daemon uptime |

### 2.2 Wallet & Earnings (`wallet`)

| Field | Type | Unit | Refresh | Capability | Description |
|---|---|---|---|---|---|
| `balance` | `Option<f64>` | USD ($) | 1s (log) | `log_parsing` | Current wallet balance parsed from log |
| `projected_24h` | `Option<f64>` | USD ($) | 1s (log) | `log_parsing` | 24-hour predicted earnings from log |
| `last_updated_at` | `Option<DateTime>` | ISO-8601 | 1s (log) | `log_parsing` | Timestamp of last wallet log line |

### 2.3 Job & Container State (`job`)

| Field | Type | Unit | Refresh | Capability | Description |
|---|---|---|---|---|---|
| `matrix_status` | `string` | — | 1s (log) | `log_parsing` | e.g. `"Idle - Searching..."`, `"Job Acquired!"` |
| `workload_count` | `u32` | count | 1s (log) | `log_parsing` | Active workloads reported by Matrix |
| `heartbeat_active` | `bool` | — | 1s (log) | `log_parsing` | `true` if Heartbeat log seen < 2 min ago |
| `id` | `Option<string>` | — | 1s (log) | `log_parsing` | Active workload/job UUID |
| `start_time` | `Option<DateTime>` | ISO-8601 | Rescan | `log_parsing` | Timestamp of earliest job assignment log |
| `uptime_seconds` | `Option<u64>` | seconds | 1s | `log_parsing` | Seconds elapsed since job start_time |
| `container_status` | `string` | — | 1s (log) | `log_parsing` | `"Pending..."`, `"Starting..."`, `"Running (Stable)"`, `"Stopped / Waiting"`, `"Network Hiccup"` |
| `download_pct` | `Option<f32>` | percent (0–100)| 1s (log) | `log_parsing` | Container image download percentage |
| `active_layer` | `Option<string>` | — | 1s (log) | `log_parsing` | 8-character hex SHA prefix of active downloading layer |
| `layer_progress` | `Option<f32>` | percent (0–100)| 1s (log) | `log_parsing` | Progress of active layer |
| `download_speed_kbps`| `Option<f32>` | KB/s | 1s | `log_parsing` | 10-sample moving average download speed |
| `download_total_mb` | `Option<f32>` | MB | 1s | `log_parsing` | Total MB downloaded in current phase |
| `download_eta_seconds`| `Option<u64>` | seconds | 1s | `log_parsing` | Estimated time remaining for container pull |

### 2.4 Hardware Metrics (`hardware`)

| Field | Type | Unit | Refresh | Capability | Description |
|---|---|---|---|---|---|
| `cpu_name` | `string` | — | Startup | None | CPU brand string |
| `cpu_load_pct` | `f32` | percent (0–100)| 10s | None | Host aggregate CPU utilization |
| `ram_used_gb` | `f32` | GB | 10s | None | Host RAM used |
| `ram_total_gb` | `f32` | GB | Startup | None | Host total physical RAM |
| `ram_load_pct` | `f32` | percent (0–100)| 10s | None | Host RAM utilization |
| `gpu_name` | `Option<string>` | — | Startup | `gpu_nvidia` | NVIDIA GPU device model |
| `gpu_uuid` | `Option<string>` | — | Startup | `gpu_nvidia` | GPU UUID |
| `gpu_utilization_pct`| `Option<u32>` | percent (0–100)| 2s | `gpu_nvidia` | GPU core compute load |
| `gpu_memory_used_mb` | `Option<u64>` | MB | 2s | `gpu_nvidia` | VRAM used |
| `gpu_memory_total_mb`| `Option<u64>` | MB | Startup | `gpu_nvidia` | VRAM total capacity |
| `gpu_power_watts` | `Option<f64>` | Watts | 2s | `gpu_nvidia` | Power draw (converted from mW) |
| `gpu_temperature_c` | `Option<u32>` | °C | 2s | `gpu_nvidia` | GPU core temperature |
| `gpu_fan_speed_pct` | `Option<u32>` | percent (0–100)| 2s | `gpu_nvidia` | GPU fan speed (optional) |
| `gpu_pcie_tx_kbps` | `Option<u64>` | KB/s | 2s | `gpu_nvidia` | PCIe transmit throughput |
| `gpu_pcie_rx_kbps` | `Option<u64>` | KB/s | 2s | `gpu_nvidia` | PCIe receive throughput |
| `disk_type` | `string` | — | Startup | None | e.g. `"NVMe SSD"`, `"SATA SSD"`, `"Disk"` |
| `disk_size_gb` | `f32` | GB | Startup | None | Total capacity of system disk |
| `disk_free_gb` | `f32` | GB | 5s | None | Free space on system disk |
| `disk_utilization_pct`| `Option<f32>` | percent (0–100)| 10s | `disk_smart` | Disk busy time percentage |
| `disk_read_mbps` | `Option<f32>` | MB/s | 10s | `disk_smart` | Disk read throughput |
| `disk_write_mbps` | `Option<f32>` | MB/s | 10s | `disk_smart` | Disk write throughput |

### 2.5 GPU Demand API (`gpu_demand`)

| Field | Type | Unit | Refresh | Capability | Description |
|---|---|---|---|---|---|
| `gpu_match_name` | `Option<string>` | — | 5m | `salad_demand_api` | Matched GPU display name from Salad API |
| `tier` | `Option<string>` | — | 5m | `salad_demand_api` | e.g. `"HIGH"`, `"MEDIUM"`, `"LOW"` |
| `utilization_pct` | `Option<f64>` | percent (0–100)| 5m | `salad_demand_api` | Network-wide active machine percentage |
| `earning_avg_24h` | `Option<f64>` | USD ($) | 5m | `salad_demand_api` | 24h network average earning rate |
| `earning_max_24h` | `Option<f64>` | USD ($) | 5m | `salad_demand_api` | 24h network peak earning rate |
| `recommended_ram_gb` | `Option<u32>` | GB | 5m | `salad_demand_api` | Recommended host RAM for matched GPU |

### 2.6 WSL Virtual Machine (`wsl`)

| Field | Type | Unit | Refresh | Capability | Description |
|---|---|---|---|---|---|
| `status` | `Option<string>` | — | 10s | `wsl_status` | `"Running (Active)"`, `"STOPPED (Offline)"` |
| `ram_mb` | `Option<f32>` | MB | 10s | `host_processes` | Working set sum of `vmmemWSL`/`vmmem`/`wslhost` |
| `disk_size_gb` | `Option<f32>` | GB | 1s (log) | `log_parsing` | Log regex `DistroSize = ...` converted to GB |

### 2.7 Network & SGS (`network`)

| Field | Type | Unit | Refresh | Capability | Description |
|---|---|---|---|---|---|
| `vnet_rx_kbps` | `Option<f32>` | KB/s | 2s | `host_nic_vethernet` | Hyper-V `vEthernet` receive throughput |
| `vnet_tx_kbps` | `Option<f32>` | KB/s | 2s | `host_nic_vethernet` | Hyper-V `vEthernet` transmit throughput |
| `vnet_total_rx_gb` | `Option<f32>` | GB | 2s | `host_nic_vethernet` | Cumulative `vEthernet` receive GB |
| `vnet_total_tx_gb` | `Option<f32>` | GB | 2s | `host_nic_vethernet` | Cumulative `vEthernet` transmit GB |
| `sgs_node_name` | `Option<string>` | — | 1s (log) | `log_parsing` | Active Bandwidth sharing node name |
| `sgs_rx_kbps` | `Option<f32>` | KB/s | 2s | `host_processes` | SGS process receive throughput |
| `sgs_tx_kbps` | `Option<f32>` | KB/s | 2s | `host_processes` | SGS process transmit throughput |
| `sgs_total_rx_mb` | `Option<f32>` | MB | 2s | `host_processes` | Cumulative SGS receive MB |
| `sgs_total_tx_mb` | `Option<f32>` | MB | 2s | `host_processes` | Cumulative SGS transmit MB |
| `sgs_ram_mb` | `Option<f32>` | MB | 2s | `host_processes` | Combined RAM working set of SGS processes |

### 2.8 Processes & Miner Detection (`process`)

| Field | Type | Unit | Refresh | Capability | Description |
|---|---|---|---|---|---|
| `salad_version` | `Option<string>` | — | 10s | `host_processes` | Salad UI version |
| `salad_uptime_seconds` | `Option<u64>` | seconds | 10s | `host_processes` | Salad UI process uptime |
| `salad_bowl_version` | `Option<string>` | — | 10s | `host_processes` | Salad Bowl Service version |
| `salad_bowl_uptime_seconds` | `Option<u64>` | seconds | 10s | `host_processes` | Salad Bowl Service uptime |
| `miner_active` | `bool` | — | 2s | `miner_detection` | `true` if active mining process identified |
| `miner_name` | `Option<string>` | — | 2s | `miner_detection` | Identified miner process name |
| `miner_scope` | `Option<string>` | — | 2s | `miner_detection` | `"INTERNAL"` (Salad tree) or `"EXTERNAL"` |

### 2.9 Log Feed & Errors (`log`)

| Field | Type | Unit | Refresh | Capability | Description |
|---|---|---|---|---|---|
| `current_logfile` | `Option<string>` | — | 1s | `log_parsing` | Current active log filename |
| `last_error` | `Option<string>` | — | 1s (log) | `log_parsing` | Text of most recent `[ERR]` log |
| `last_warning` | `Option<string>` | — | 1s (log) | `log_parsing` | Text of most recent `[WRN]` log |
| `recent_logs` | `Vec<string>` | — | 1s (log) | `log_parsing` | Rolling ring buffer of last 4 log lines |

---

## 3. In-RAM Ring Buffers (Graph History)

To power real-time UI charts without SQLite disk writes, the daemon maintains bounded `VecDeque` ring buffers in memory:

| Metric Series | Max Capacity | Sample Interval | Duration Retained |
|---|---|---|---|
| `gpu_utilization_history` | 360 samples | 2s | 12 minutes |
| `gpu_power_history` | 360 samples | 2s | 12 minutes |
| `cpu_load_history` | 360 samples | 2s | 12 minutes |
| `download_speed_history` | 360 samples | 2s | 12 minutes |
| `vnet_throughput_history` | 360 samples | 2s | 12 minutes |

When a new client connects over SSE (`/api/v1/stream`), the daemon immediately transmits the current `Snapshot` along with the full contents of these ring buffers in the initial `snapshot` event. Subsequent ticks transmit compact `delta` events containing only updated values.
