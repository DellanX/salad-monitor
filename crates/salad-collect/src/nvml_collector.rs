//! NVIDIA GPU telemetry collector using `nvml-wrapper` (v0.13).
//!
//! Uses dynamic dlopen (`nvml.dll` / `libnvidia-ml.so.1`) so no CUDA SDK is needed.
//! Gracefully disables itself if NVML is not available on the host/container.

use nvml_wrapper::enum_wrappers::device::Clock;
use nvml_wrapper::enums::device::TemperatureSensor;
use nvml_wrapper::Nvml;
use serde::{Deserialize, Serialize};
use std::sync::OnceLock;

static NVML_INSTANCE: OnceLock<Option<Nvml>> = OnceLock::new();

fn get_nvml() -> &'static Option<Nvml> {
    NVML_INSTANCE.get_or_init(|| match Nvml::init() {
        Ok(nvml) => Some(nvml),
        Err(e) => {
            eprintln!("NVML initialization skipped/failed: {}", e);
            None
        }
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuProcessInfo {
    pub pid: u32,
    pub used_memory_bytes: Option<u64>,
    pub process_type: String, // "compute" or "graphics"
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuDeviceMetrics {
    pub uuid: String,
    pub index: u32,
    pub name: String,
    pub gpu_utilization_pct: u32,
    pub memory_utilization_pct: u32,
    pub memory_total_bytes: u64,
    pub memory_used_bytes: u64,
    pub memory_free_bytes: u64,
    pub temperature_c: u32,
    pub power_usage_w: f32,
    pub power_limit_w: Option<f32>,
    pub fan_speed_pct: Option<u32>,
    pub clock_sm_mhz: Option<u32>,
    pub clock_memory_mhz: Option<u32>,
    pub pcie_tx_kbps: Option<u32>,
    pub pcie_rx_kbps: Option<u32>,
    pub running_processes: Vec<GpuProcessInfo>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuTelemetrySnapshot {
    pub is_available: bool,
    pub devices: Vec<GpuDeviceMetrics>,
}

pub struct NvmlCollector;

impl NvmlCollector {
    pub fn new() -> Self {
        Self
    }

    /// Check if NVML is present and working on this system.
    pub fn is_available() -> bool {
        get_nvml().is_some()
    }

    /// Collect GPU metrics across all available NVIDIA GPUs.
    pub fn collect(&self) -> GpuTelemetrySnapshot {
        let nvml = match get_nvml() {
            Some(n) => n,
            None => {
                return GpuTelemetrySnapshot {
                    is_available: false,
                    devices: Vec::new(),
                }
            }
        };

        let device_count = match nvml.device_count() {
            Ok(count) => count,
            Err(_) => {
                return GpuTelemetrySnapshot {
                    is_available: false,
                    devices: Vec::new(),
                }
            }
        };

        let mut devices = Vec::new();

        for idx in 0..device_count {
            if let Ok(device) = nvml.device_by_index(idx) {
                let uuid = device
                    .uuid()
                    .unwrap_or_else(|_| format!("GPU-INDEX-{}", idx));
                let name = device
                    .name()
                    .unwrap_or_else(|_| "Unknown NVIDIA GPU".to_string());

                let util = device.utilization_rates().ok();
                let gpu_util = util.map(|u| u.gpu).unwrap_or(0);
                let mem_util = util.map(|u| u.memory).unwrap_or(0);

                let mem_info = device.memory_info().ok();
                let mem_total = mem_info.map(|m| m.total).unwrap_or(0);
                let mem_used = mem_info.map(|m| m.used).unwrap_or(0);
                let mem_free = mem_info.map(|m| m.free).unwrap_or(0);

                let temp = device
                    .temperature(TemperatureSensor::Gpu)
                    .unwrap_or(0);

                let power_mW = device.power_usage().ok();
                let power_w = power_mW.map(|p| p as f32 / 1000.0).unwrap_or(0.0);

                let power_limit_mW = device.enforced_power_limit().ok();
                let power_limit_w = power_limit_mW.map(|p| p as f32 / 1000.0);

                let fan_speed = device.fan_speed(0).ok();
                let sm_clock = device.clock_info(Clock::SM).ok();
                let mem_clock = device.clock_info(Clock::Memory).ok();

                let pcie_tx = device
                    .pcie_throughput(nvml_wrapper::enum_wrappers::device::PcieUtilCounter::Send)
                    .ok();
                let pcie_rx = device
                    .pcie_throughput(
                        nvml_wrapper::enum_wrappers::device::PcieUtilCounter::Receive,
                    )
                    .ok();

                // Processes
                let mut processes = Vec::new();
                if let Ok(compute_procs) = device.running_compute_processes() {
                    for proc in compute_procs {
                        let mem = match proc.used_gpu_memory {
                            nvml_wrapper::struct_wrappers::device::UsedGpuMemory::Used(b) => {
                                Some(b)
                            }
                            nvml_wrapper::struct_wrappers::device::UsedGpuMemory::Unavailable => {
                                None
                            }
                        };
                        processes.push(GpuProcessInfo {
                            pid: proc.pid,
                            used_memory_bytes: mem,
                            process_type: "compute".to_string(),
                        });
                    }
                }

                if let Ok(graphics_procs) = device.running_graphics_processes() {
                    for proc in graphics_procs {
                        let mem = match proc.used_gpu_memory {
                            nvml_wrapper::struct_wrappers::device::UsedGpuMemory::Used(b) => {
                                Some(b)
                            }
                            nvml_wrapper::struct_wrappers::device::UsedGpuMemory::Unavailable => {
                                None
                            }
                        };
                        processes.push(GpuProcessInfo {
                            pid: proc.pid,
                            used_memory_bytes: mem,
                            process_type: "graphics".to_string(),
                        });
                    }
                }

                devices.push(GpuDeviceMetrics {
                    uuid,
                    index: idx,
                    name,
                    gpu_utilization_pct: gpu_util,
                    memory_utilization_pct: mem_util,
                    memory_total_bytes: mem_total,
                    memory_used_bytes: mem_used,
                    memory_free_bytes: mem_free,
                    temperature_c: temp,
                    power_usage_w: power_w,
                    power_limit_w,
                    fan_speed_pct: fan_speed,
                    clock_sm_mhz: sm_clock,
                    clock_memory_mhz: mem_clock,
                    pcie_tx_kbps: pcie_tx,
                    pcie_rx_kbps: pcie_rx,
                    running_processes: processes,
                });
            }
        }

        GpuTelemetrySnapshot {
            is_available: true,
            devices,
        }
    }
}

