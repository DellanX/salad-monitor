# `salad-collect` Library Crate Specification

`salad-collect` provides platform-abstracted telemetry collectors.

## Modules:
- `sysinfo_collector`: Cross-platform CPU, RAM, disk, network, and system uptime queries via `sysinfo`.
- `nvml_collector`: NVIDIA GPU telemetry via `nvml-wrapper` 0.13 (`dlopen` runtime loading).
- `demand_api`: HTTP client fetching GPU pricing and demand tiers from `https://app-api.salad.com/api/v2/demand-monitor/gpu`.
- `windows_collector`: Windows-specific WMI, registry, and WSL queries (`cfg(windows)`).
