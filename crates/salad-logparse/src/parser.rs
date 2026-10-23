//! Regex line parser for Salad Bowl log files.

use chrono::{DateTime, NaiveDateTime, Utc};
use once_cell::sync::Lazy;
use regex::Regex;

static RE_TIMESTAMP: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})").unwrap()
});

static RE_MATRIX_STATE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"Received desired state from matrix - (\d+) workloads").unwrap()
});

static RE_WALLET: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"Wallet: Current\((.*?)\), Predicted\((.*?)\)").unwrap()
});

static RE_WORKLOAD_ID: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"salad\.com/sce/([a-f0-9\-]+)").unwrap()
});

static RE_LAYER_PROGRESS: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"Pull progress event: .*?@sha256:([a-f0-9]{8})[a-f0-9]*\s([0-9.]+)").unwrap()
});

static RE_GLOBAL_PROGRESS: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"Progress\((0[,.]\d+|1[,.]0+)\)").unwrap()
});

static RE_BANDWIDTH_NODE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"(Bandwidth-[a-zA-Z0-9\-]+)").unwrap()
});

static RE_ERROR_WARNING: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"\[(WRN|ERR)\]\s+(.*)").unwrap()
});

static RE_DISTRO_SIZE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"DistroSize\s*=\s*([0-9.]+)").unwrap()
});

/// Extracted log event types.
#[derive(Debug, Clone, PartialEq)]
pub enum LogEvent {
    Timestamp(DateTime<Utc>),
    MatrixState { workload_count: u32 },
    Wallet { balance: f64, projected: f64 },
    WorkloadId(String),
    LayerProgress { layer_sha: String, progress: f32 },
    GlobalProgress(f32),
    RunningStatus,
    KilledStatus,
    BandwidthNode(String),
    StopBandwidthWorkload,
    Warning(String),
    Error(String),
    Heartbeat,
    DistroSizeGb(f32),
    Unmatched,
}

/// Parse a single Salad Bowl log line.
/// Guaranteed never to panic; degrades to `LogEvent::Unmatched` on invalid formats.
pub fn parse_log_line(line: &str) -> LogEvent {
    let line = line.trim();
    if line.is_empty() {
        return LogEvent::Unmatched;
    }

    // Matrix state
    if let Some(cap) = RE_MATRIX_STATE.captures(line) {
        if let Ok(count) = cap[1].parse::<u32>() {
            return LogEvent::MatrixState { workload_count: count };
        }
    }

    // Wallet info
    if let Some(cap) = RE_WALLET.captures(line) {
        let bal = cap[1].replace(',', ".").parse::<f64>().unwrap_or(0.0);
        let proj = cap[2].replace(',', ".").parse::<f64>().unwrap_or(0.0);
        return LogEvent::Wallet { balance: bal, projected: proj };
    }

    // Workload / Job ID (ignore lines with TTL or pullDuration)
    if !line.contains("TTL =") && !line.contains("pullDuration") {
        if let Some(cap) = RE_WORKLOAD_ID.captures(line) {
            return LogEvent::WorkloadId(cap[1].to_string());
        }
    }

    // Layer pull progress
    if let Some(cap) = RE_LAYER_PROGRESS.captures(line) {
        let sha = cap[1].to_string();
        let pct = cap[2].replace(',', ".").parse::<f32>().unwrap_or(0.0) * 100.0;
        return LogEvent::LayerProgress { layer_sha: sha, progress: pct };
    }

    // Overall pull progress
    if let Some(cap) = RE_GLOBAL_PROGRESS.captures(line) {
        let pct = cap[1].replace(',', ".").parse::<f32>().unwrap_or(0.0) * 100.0;
        return LogEvent::GlobalProgress(pct);
    }

    // Running status
    if line.contains("Running(Ready") || line.contains("already running") || line.contains("already installed") {
        return LogEvent::RunningStatus;
    }

    // Killed / failed status
    if line.contains("Killed") || line.contains("Stopped") || line.contains("failed") {
        if line.contains("Stopping workload") && line.contains("Bandwidth") {
            return LogEvent::StopBandwidthWorkload;
        }
        return LogEvent::KilledStatus;
    }

    // Bandwidth node
    if let Some(cap) = RE_BANDWIDTH_NODE.captures(line) {
        return LogEvent::BandwidthNode(cap[1].to_string());
    }

    // Heartbeat
    if line.contains("Heartbeat") {
        return LogEvent::Heartbeat;
    }

    // Distro size
    if let Some(cap) = RE_DISTRO_SIZE.captures(line) {
        if let Ok(bytes) = cap[1].parse::<f64>() {
            let gb = (bytes / 1_073_741_824.0) as f32;
            return LogEvent::DistroSizeGb(gb);
        }
    }

    // Warning / Error
    if let Some(cap) = RE_ERROR_WARNING.captures(line) {
        let level = &cap[1];
        let msg = cap[2].trim().to_string();
        return match level {
            "WRN" => LogEvent::Warning(msg),
            "ERR" => LogEvent::Error(msg),
            _ => LogEvent::Unmatched,
        };
    }

    LogEvent::Unmatched
}

/// Extract timestamp from log line.
pub fn extract_timestamp(line: &str) -> Option<DateTime<Utc>> {
    RE_TIMESTAMP.captures(line).and_then(|cap| {
        NaiveDateTime::parse_from_str(&cap[1], "%Y-%m-%d %H:%M:%S")
            .ok()
            .map(|ndt| DateTime::<Utc>::from_naive_utc_and_offset(ndt, Utc))
    })
}

