//! Telemetry snapshot, ring buffers, and SSE broadcast channel.

use salad_collect::demand_api::GpuDemandInfo;
use salad_collect::nvml_collector::GpuTelemetrySnapshot;
use salad_collect::sysinfo_collector::SystemTelemetrySnapshot;
use salad_logparse::state_machine::LogStateSnapshot;
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::sync::{Arc, RwLock};
use tokio::sync::broadcast;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Capabilities {
    pub log_parsing: bool,
    pub salad_demand_api: bool,
    pub gpu_nvidia: bool,
    pub gpu_per_process: bool,
    pub miner_detection: bool,
    pub host_processes: bool,
    pub wsl_status: bool,
    pub windows_registry: bool,
    pub host_nic_vethernet: bool,
    pub disk_smart: bool,
}

impl Default for Capabilities {
    fn default() -> Self {
        let is_windows = cfg!(windows);
        Self {
            log_parsing: true,
            salad_demand_api: true,
            gpu_nvidia: false, // Set dynamically at startup via NvmlCollector::is_available()
            gpu_per_process: is_windows,
            miner_detection: is_windows,
            host_processes: is_windows,
            wsl_status: is_windows,
            windows_registry: is_windows,
            host_nic_vethernet: is_windows,
            disk_smart: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricSample {
    pub timestamp_secs: i64,
    pub cpu_usage_pct: f32,
    pub memory_usage_pct: f32,
    pub gpu_usage_pct: Option<u32>,
    pub gpu_temp_c: Option<u32>,
    pub power_w: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UnifiedSnapshot {
    pub timestamp: i64,
    pub capabilities: Capabilities,
    pub system: Option<SystemTelemetrySnapshot>,
    pub gpu: Option<GpuTelemetrySnapshot>,
    pub log_state: LogStateSnapshot,
    pub demand: Vec<GpuDemandInfo>,
    pub history: Vec<MetricSample>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum SseEvent {
    Snapshot(UnifiedSnapshot),
    Heartbeat(i64),
    LogLine(String),
}

pub struct AppState {
    pub current_snapshot: RwLock<UnifiedSnapshot>,
    pub ring_buffer: RwLock<VecDeque<MetricSample>>,
    pub broadcaster: broadcast::Sender<SseEvent>,
}

impl AppState {
    pub fn new(capabilities: Capabilities) -> Arc<Self> {
        let (tx, _) = broadcast::channel(100);

        let initial_snapshot = UnifiedSnapshot {
            timestamp: chrono::Utc::now().timestamp(),
            capabilities,
            system: None,
            gpu: None,
            log_state: LogStateSnapshot::default(),
            demand: Vec::new(),
            history: Vec::new(),
        };

        Arc::new(Self {
            current_snapshot: RwLock::new(initial_snapshot),
            ring_buffer: RwLock::new(VecDeque::with_capacity(360)),
            broadcaster: tx,
        })
    }

    pub fn push_sample(&self, sample: MetricSample) {
        let mut history = self.ring_buffer.write().unwrap();
        if history.len() >= 360 {
            history.pop_front();
        }
        history.push_back(sample);

        let mut snap = self.current_snapshot.write().unwrap();
        snap.history = history.iter().cloned().collect();
    }

    pub fn get_snapshot(&self) -> UnifiedSnapshot {
        self.current_snapshot.read().unwrap().clone()
    }
}
