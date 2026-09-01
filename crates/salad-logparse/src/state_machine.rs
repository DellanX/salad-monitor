//! Workload state machine and download progress / ETA calculator.

use crate::parser::{parse_log_line, LogEvent};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum WorkloadStatus {
    Idle,
    Downloading,
    Running,
    Killed,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LayerProgressInfo {
    pub layer_sha: String,
    pub progress: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogStateSnapshot {
    pub status: WorkloadStatus,
    pub workload_id: Option<String>,
    pub global_progress: f32,
    pub layer_progress: Vec<LayerProgressInfo>,
    pub download_speed_pct_per_sec: f32,
    pub eta_seconds: Option<u64>,
    pub wallet_balance: f64,
    pub wallet_projected: f64,
    pub bandwidth_node: Option<String>,
    pub distro_size_gb: Option<f32>,
    pub active_workloads_count: u32,
    pub recent_errors: Vec<String>,
    pub recent_warnings: Vec<String>,
    pub last_heartbeat: Option<DateTime<Utc>>,
}

impl Default for LogStateSnapshot {
    fn default() -> Self {
        Self {
            status: WorkloadStatus::Idle,
            workload_id: None,
            global_progress: 0.0,
            layer_progress: Vec::new(),
            download_speed_pct_per_sec: 0.0,
            eta_seconds: None,
            wallet_balance: 0.0,
            wallet_projected: 0.0,
            bandwidth_node: None,
            distro_size_gb: None,
            active_workloads_count: 0,
            recent_errors: Vec::new(),
            recent_warnings: Vec::new(),
            last_heartbeat: None,
        }
    }
}

/// State machine tracking Salad Bowl log events.
pub struct LogStateMachine {
    state: LogStateSnapshot,
    layers: HashMap<String, f32>,
    progress_history: VecDeque<(DateTime<Utc>, f32)>,
}

impl LogStateMachine {
    pub fn new() -> Self {
        Self {
            state: LogStateSnapshot::default(),
            layers: HashMap::new(),
            progress_history: VecDeque::with_capacity(30),
        }
    }

    /// Process a line from the log file.
    pub fn process_line(&mut self, line: &str) {
        let event = parse_log_line(line);
        self.process_event(event);
    }

    /// Process a parsed `LogEvent`.
    pub fn process_event(&mut self, event: LogEvent) {
        match event {
            LogEvent::Timestamp(ts) => {
                self.state.last_heartbeat = Some(ts);
            }
            LogEvent::MatrixState { workload_count } => {
                self.state.active_workloads_count = workload_count;
                if workload_count == 0 {
                    self.state.status = WorkloadStatus::Idle;
                }
            }
            LogEvent::Wallet { balance, projected } => {
                self.state.wallet_balance = balance;
                self.state.wallet_projected = projected;
            }
            LogEvent::WorkloadId(id) => {
                if self.state.workload_id.as_deref() != Some(&id) {
                    self.state.workload_id = Some(id);
                    self.layers.clear();
                    self.state.global_progress = 0.0;
                    self.progress_history.clear();
                    self.state.status = WorkloadStatus::Downloading;
                }
            }
            LogEvent::LayerProgress { layer_sha, progress } => {
                self.layers.insert(layer_sha, progress);
                self.state.status = WorkloadStatus::Downloading;
            }
            LogEvent::GlobalProgress(pct) => {
                self.state.global_progress = pct;
                self.state.status = WorkloadStatus::Downloading;

                let now = Utc::now();
                self.progress_history.push_back((now, pct));
                if self.progress_history.len() > 20 {
                    self.progress_history.pop_front();
                }
                self.recalculate_eta();
            }
            LogEvent::RunningStatus => {
                self.state.status = WorkloadStatus::Running;
                self.state.global_progress = 100.0;
                self.state.eta_seconds = Some(0);
            }
            LogEvent::KilledStatus => {
                self.state.status = WorkloadStatus::Killed;
            }
            LogEvent::BandwidthNode(node) => {
                self.state.bandwidth_node = Some(node);
            }
            LogEvent::StopBandwidthWorkload => {
                self.state.bandwidth_node = None;
            }
            LogEvent::Warning(msg) => {
                if self.state.recent_warnings.len() >= 10 {
                    self.state.recent_warnings.remove(0);
                }
                self.state.recent_warnings.push(msg);
            }
            LogEvent::Error(msg) => {
                if self.state.recent_errors.len() >= 10 {
                    self.state.recent_errors.remove(0);
                }
                self.state.recent_errors.push(msg);
            }
            LogEvent::Heartbeat => {
                self.state.last_heartbeat = Some(Utc::now());
            }
            LogEvent::DistroSizeGb(gb) => {
                self.state.distro_size_gb = Some(gb);
            }
            LogEvent::Unmatched => {}
        }

        // Sync layer vector
        self.state.layer_progress = self
            .layers
            .iter()
            .map(|(k, v)| LayerProgressInfo {
                layer_sha: k.clone(),
                progress: *v,
            })
            .collect();
    }

    fn recalculate_eta(&mut self) {
        if self.progress_history.len() < 2 {
            self.state.download_speed_pct_per_sec = 0.0;
            self.state.eta_seconds = None;
            return;
        }

        let first = self.progress_history.front().unwrap();
        let last = self.progress_history.back().unwrap();

        let duration_secs = (last.0 - first.0).num_milliseconds() as f32 / 1000.0;
        let progress_diff = last.1 - first.1;

        if duration_secs > 0.0 && progress_diff > 0.0 {
            let speed = progress_diff / duration_secs;
            self.state.download_speed_pct_per_sec = speed;

            let remaining_pct = 100.0 - last.1;
            if remaining_pct > 0.0 && speed > 0.0 {
                let eta = (remaining_pct / speed).ceil() as u64;
                self.state.eta_seconds = Some(eta);
            } else {
                self.state.eta_seconds = Some(0);
            }
        }
    }

    pub fn snapshot(&self) -> LogStateSnapshot {
        self.state.clone()
    }
}

