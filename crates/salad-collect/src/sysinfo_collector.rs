//! Cross-platform system telemetry collector using sysinfo.

use serde::{Deserialize, Serialize};
use std::time::Instant;
use sysinfo::{CpuRefreshKind, Disks, Networks, System};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CpuMetrics {
    pub usage_pct: f32,
    pub core_count: usize,
    pub brand: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryMetrics {
    pub total_bytes: u64,
    pub used_bytes: u64,
    pub free_bytes: u64,
    pub usage_pct: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiskMetrics {
    pub name: String,
    pub mount_point: String,
    pub total_bytes: u64,
    pub available_bytes: u64,
    pub usage_pct: f32,
    pub is_removable: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkMetrics {
    pub interface_name: String,
    pub total_rx_bytes: u64,
    pub total_tx_bytes: u64,
    pub rx_rate_bytes_per_sec: f64,
    pub tx_rate_bytes_per_sec: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemInfo {
    pub hostname: String,
    pub os_name: String,
    pub os_version: String,
    pub kernel_version: String,
    pub arch: String,
    pub uptime_secs: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemTelemetrySnapshot {
    pub system_info: SystemInfo,
    pub cpu: CpuMetrics,
    pub memory: MemoryMetrics,
    pub disks: Vec<DiskMetrics>,
    pub networks: Vec<NetworkMetrics>,
}

pub struct SysinfoCollector {
    sys: System,
    disks: Disks,
    networks: Networks,
    last_network_check: Instant,
    last_network_snapshot: std::collections::HashMap<String, (u64, u64)>,
}

impl SysinfoCollector {
    pub fn new() -> Self {
        let mut sys = System::new_all();
        sys.refresh_cpu_specifics(CpuRefreshKind::everything());
        sys.refresh_memory();

        let disks = Disks::new_with_refreshed_list();
        let networks = Networks::new_with_refreshed_list();

        Self {
            sys,
            disks,
            networks,
            last_network_check: Instant::now(),
            last_network_snapshot: std::collections::HashMap::new(),
        }
    }

    pub fn collect(&mut self) -> SystemTelemetrySnapshot {
        // Refresh CPU & Memory
        self.sys.refresh_cpu_specifics(CpuRefreshKind::everything());
        self.sys.refresh_memory();
        self.disks.refresh();
        self.networks.refresh();

        let cpu_usage = self.sys.global_cpu_info().cpu_usage();
        let cpu_brand = self
            .sys
            .cpus()
            .first()
            .map(|c| c.brand().to_string())
            .unwrap_or_else(|| "Unknown".to_string());
        let core_count = self.sys.cpus().len();

        let cpu = CpuMetrics {
            usage_pct: cpu_usage,
            core_count,
            brand: cpu_brand,
        };

        let total_mem = self.sys.total_memory();
        let used_mem = self.sys.used_memory();
        let free_mem = self.sys.free_memory();
        let mem_pct = if total_mem > 0 {
            (used_mem as f32 / total_mem as f32) * 100.0
        } else {
            0.0
        };

        let memory = MemoryMetrics {
            total_bytes: total_mem,
            used_bytes: used_mem,
            free_bytes: free_mem,
            usage_pct: mem_pct,
        };

        let disks = self
            .disks
            .iter()
            .map(|d| {
                let total = d.total_space();
                let avail = d.available_space();
                let used = total.saturating_sub(avail);
                let pct = if total > 0 {
                    (used as f32 / total as f32) * 100.0
                } else {
                    0.0
                };

                DiskMetrics {
                    name: d.name().to_string_lossy().to_string(),
                    mount_point: d.mount_point().to_string_lossy().to_string(),
                    total_bytes: total,
                    available_bytes: avail,
                    usage_pct: pct,
                    is_removable: d.is_removable(),
                }
            })
            .collect();

        let now = Instant::now();
        let elapsed_secs = now.duration_since(self.last_network_check).as_secs_f64();
        let mut network_metrics = Vec::new();

        for (interface_name, net) in self.networks.iter() {
            let rx = net.total_received();
            let tx = net.total_transmitted();

            let (rx_rate, tx_rate) = if elapsed_secs > 0.0 {
                if let Some(&(prev_rx, prev_tx)) = self.last_network_snapshot.get(interface_name) {
                    let rx_diff = rx.saturating_sub(prev_rx) as f64;
                    let tx_diff = tx.saturating_sub(prev_tx) as f64;
                    (rx_diff / elapsed_secs, tx_diff / elapsed_secs)
                } else {
                    (0.0, 0.0)
                }
            } else {
                (0.0, 0.0)
            };

            self.last_network_snapshot.insert(interface_name.clone(), (rx, tx));

            network_metrics.push(NetworkMetrics {
                interface_name: interface_name.clone(),
                total_rx_bytes: rx,
                total_tx_bytes: tx,
                rx_rate_bytes_per_sec: rx_rate,
                tx_rate_bytes_per_sec: tx_rate,
            });
        }

        self.last_network_check = now;

        let system_info = SystemInfo {
            hostname: System::host_name().unwrap_or_else(|| "localhost".to_string()),
            os_name: System::name().unwrap_or_else(|| "Unknown".to_string()),
            os_version: System::os_version().unwrap_or_else(|| "Unknown".to_string()),
            kernel_version: System::kernel_version().unwrap_or_else(|| "Unknown".to_string()),
            arch: System::cpu_arch().unwrap_or_else(|| "Unknown".to_string()),
            uptime_secs: System::uptime(),
        };

        SystemTelemetrySnapshot {
            system_info,
            cpu,
            memory,
            disks,
            networks: network_metrics,
        }
    }
}

