# SaladXRay Parity Specification (`docs/parity.md`)

This document details feature-by-feature parity between [joseluisfreire/SaladXRay](https://github.com/joseluisfreire/SaladXRay) and `salad-monitor` v1.0.

## Overview

SaladXRay is a Windows C# TUI application that monitors a local Salad node. `salad-monitor` v1.0 achieves parity with SaladXRay's core monitoring capabilities while providing a modern web UI, cross-platform container support (via capability degradation), SSE streaming, and webhook integrations.

---

## Panel Mapping & Feature Matrix

| SaladXRay Panel | Label / Data Point | SaladXRay Source | `salad-monitor` Target Field | Capability Required | Notes / Parity Status |
|---|---|---|---|---|---|
| **Header Banner** | App Version | Process enum / HKCU Registry | `process.salad_version` | `windows_registry` / `host_processes` | Full on Windows; `null` in container unless env override provided |
| | Svc Version | Process enum / HKLM Registry | `process.salad_bowl_version` | `windows_registry` / `host_processes` | Full on Windows; `null` in container unless env override provided |
| | OS Version | HKLM NT Registry | `system.os_version` | `sysinfo` (Cross-platform) | Replaced Windows Registry lookup with `sysinfo::System::os_version` |
| | Reading Log | `Path.GetFileName` log file | `log.current_logfile` | `log_parsing` | 100% Parity |
| **Uptime** | App Uptime | `Process.StartTime` | `process.salad_uptime_seconds` | `host_processes` | Full on Windows |
| | Svc Uptime | `Process.StartTime` / WMI | `process.salad_bowl_uptime_seconds` | `host_processes` | Full on Windows |
| | OS Uptime | `Environment.TickCount64` | `system.uptime_seconds` | Cross-platform | `sysinfo::System::uptime()` |
| | Daemon Uptime | `appStartTime` | `system.daemon_uptime_seconds` | Cross-platform | Process start time |
| **Earnings** | Wallet Balance | Log regex `Wallet: Current(...)` | `wallet.balance` | `log_parsing` | 100% Parity |
| | 24H EST | Log regex `Wallet: Predicted(...)` | `wallet.projected_24h` | `log_parsing` | 100% Parity |
| | Last Update | Log line timestamp | `wallet.last_updated_at` | `log_parsing` | 100% Parity |
| **Linux WSL** | VM Status | `wsl.exe -l -v` stdout regex | `wsl.status` | `wsl_status` | Windows Native only (`null` in container) |
| | VM RAM | `vmmemWSL`/`vmmem` WorkingSet | `wsl.ram_mb` | `host_processes` | Windows Native only (`null` in container) |
| | VM Disk | Log regex `DistroSize = ...` | `wsl.disk_size_gb` | `log_parsing` | 100% Parity (log-derived!) |
| | VM LAN | `vEthernet*` NIC statistics | `wsl.vnet_rx_kbps`, `tx`, `totals` | `host_nic_vethernet` | Windows Native only |
| **Container Workload** | Matrix State | Log regex `Received desired state...` | `job.matrix_status`, `workload_count` | `log_parsing` | 100% Parity |
| | Heartbeat | Log line substring `"Heartbeat"` | `job.heartbeat_active` | `log_parsing` | 100% Parity |
| | Workload ID | Log regex `salad.com/sce/...` | `job.id` | `log_parsing` | 100% Parity |
| | Workload Start Time | Log scan rescan | `job.start_time` | `log_parsing` | 100% Parity |
| | Container Status | Log regexes & progress state | `job.container_status` | `log_parsing` | 100% Parity |
| | Download Progress | Log regex `Progress(...)` & SHA | `job.download_pct`, `speed`, `eta` | `log_parsing` | 100% Parity |
| | Container Uptime | Time since `job.start_time` | `job.uptime_seconds` | `log_parsing` | 100% Parity |
| **Global Hardware** | CPU Load & Name | WMI `Win32_Processor` | `hardware.cpu_name`, `load_pct` | `sysinfo` (Cross-platform) | Replaced WMI with `sysinfo` cross-platform CPU queries |
| | GPU Stats | `nvidia-smi` / WMI fallback | `hardware.gpu_name`, `util`, `temp`, `watts`, etc. | `gpu_nvidia` | **Enhanced**: `nvml-wrapper` 0.13 used natively and in GPU containers |
| | RAM Used / Total | WMI `Win32_OperatingSystem` | `hardware.ram_used_gb`, `total`, `pct` | `sysinfo` (Cross-platform) | Replaced WMI with `sysinfo` cross-platform memory queries |
| | Host Disk | WMI `MSFT_PhysicalDisk` & `PerfDisk` | `hardware.disk_type`, `size`, `free`, `io` | `sysinfo` / `disk_smart` | Cross-platform disk queries with `sysinfo` |
| **Salad GPU Demand** | Demand Tier & RAM | `app-api.salad.com` HTTP API | `gpu_demand.tier`, `recommended_ram_gb` | `salad_demand_api` | 100% Parity |
| | Net Utilization | `app-api.salad.com` HTTP API | `gpu_demand.utilization_pct` | `salad_demand_api` | 100% Parity |
| | 24H Earning Avg/Max | `app-api.salad.com` HTTP API | `gpu_demand.earning_avg_24h`, `max_24h` | `salad_demand_api` | 100% Parity |
| **Windows Workloads** | GPU Miner / Anti-cheat | Process enum + PerfCounter | `process.miner_active`, `miner_name` | `gpu_per_process` | **Enhanced**: NVML compute/graphics process classification replaces WMI/PerfCounter |
| | SGS Node Name | Log regex `Bandwidth-...` | `network.sgs_node_name` | `log_parsing` | 100% Parity |
| | SGS Network I/O & RAM | Process enum (`sgs*`, `v2ray*`) | `network.sgs_rx_kbps`, `tx`, `ram_mb` | `host_processes` | Windows Native / `--pid=host` |
| **Recent Events** | Error / Warning | Log lines `[ERR]` / `[WRN]` | `log.last_error`, `last_warning` | `log_parsing` | 100% Parity |
| | Recent Logs Feed | Tail last 4 lines | `log.recent_logs` | `log_parsing` | 100% Parity |

---

## Log Regex Specifications

The log parser ports all 12 SaladXRay patterns verbatim:

1. **Log Line Timestamp**: `r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"`
2. **Matrix Workload Count**: `r"Received desired state from matrix - (\d+) workloads"`
3. **Wallet Balance & Projected**: `r"Wallet: Current\((.*?)\), Predicted\((.*?)\)"`
4. **Workload / Job ID**: `r"salad\.com/sce/([a-f0-9\-]+)"` (excluding lines containing `TTL =` or `pullDuration`)
5. **Layer Download Progress**: `r"Pull progress event: .*?@sha256:([a-f0-9]{8})[a-f0-9]*\s([0-9.]+)"`
6. **Overall Pull Progress**: `r"Progress\((0[,.]\d+|1[,.]0+)\)"`
7. **Running Status**: Substring match `"Running(Ready"`, `"already running"`, or `"already installed"`
8. **Killed / Retrying Status**: Substring match `"Killed"`, `"Stopped"`, or `"failed"`
9. **Bandwidth / SGS Node**: `r"(Bandwidth-[a-zA-Z0-9\-]+)"`
10. **Stopping Bandwidth Workload**: Substrings `"Stopping workload"` AND `"Bandwidth"`
11. **Error / Warning Logs**: `r"\[(?:WRN|ERR)\]\s+(.*)"`
12. **WSL Distro Size**: `r"DistroSize\s*=\s*([0-9.]+)"`

---

## Accepted Gaps & Rejections

1. **AMD GPU Telemetry**: SaladXRay falls back to WMI `Win32_VideoController` and Windows `PerformanceCounter("GPU Engine")` for AMD load. AMD telemetry is Linux-only in Rust (`libdrm` / sysfs) and unavailable on Windows natively. AMD is explicitly excluded from `salad-monitor` v1.0. Non-NVIDIA systems report `gpu_nvidia: false` with GPU telemetry disabled.
2. **TUI-Only Features**: FIGlet ASCII header font, terminal zoom hotkeys (`Ctrl +/-`), legacy Windows 10 emoji shortcode replacements, and Spectre.Console styling are obsolete and excluded in favor of the Vue 3 web UI.
3. **PE File Version Reading**: `FileVersionInfo.GetVersionInfo` on `.exe` binaries is Windows-only. Replaced with `sysinfo` process inspection and environment variable fallbacks.
