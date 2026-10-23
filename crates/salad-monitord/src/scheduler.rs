//! Periodic background telemetry collection, log tailing, and snapshot update loops.

use crate::state::{AppState, MetricSample, SseEvent};
use salad_collect::nvml_collector::NvmlCollector;
use salad_collect::sysinfo_collector::SysinfoCollector;
use salad_logparse::state_machine::LogStateMachine;
use salad_logparse::tailer::LogTailer;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::time::{sleep, Duration};

pub fn start_scheduler(state: Arc<AppState>, log_dir: PathBuf) {
    // 1-second metrics collection loop
    let state_clone = Arc::clone(&state);
    tokio::spawn(async move {
        let mut sys_collector = SysinfoCollector::new();
        let nvml_collector = NvmlCollector::new();

        loop {
            let sys_snap = sys_collector.collect();
            let gpu_snap = nvml_collector.collect();
            let now = chrono::Utc::now().timestamp();

            let sample = MetricSample {
                timestamp_secs: now,
                cpu_usage_pct: sys_snap.cpu.usage_pct,
                memory_usage_pct: sys_snap.memory.usage_pct,
                gpu_usage_pct: gpu_snap.devices.first().map(|d| d.gpu_utilization_pct),
                gpu_temp_c: gpu_snap.devices.first().map(|d| d.temperature_c),
                gpu_memory_pct: gpu_snap.devices.first().map(|d| d.memory_utilization_pct as f32),
                power_w: gpu_snap.devices.first().map(|d| d.power_usage_w),
            };

            state_clone.push_sample(sample);

            {
                let mut snap = state_clone.current_snapshot.write().unwrap();
                snap.timestamp = now;
                snap.system = Some(sys_snap);
                snap.gpu = Some(gpu_snap);
            }

            // Broadcast the snapshot event
            let snapshot_event = SseEvent::Snapshot(state_clone.get_snapshot());
            // Suppress errors when there are no subscribers to avoid spam in logs
            let _ = state_clone.broadcaster.send(snapshot_event);

            sleep(Duration::from_secs(1)).await;
        }
    });

    // 2-second log tailing loop
    let state_clone = Arc::clone(&state);
    tokio::spawn(async move {
        let mut tailer = LogTailer::new(log_dir);
        let mut state_machine = LogStateMachine::new();

        loop {
            let lines = tailer.read_new_lines();
            for line in lines {
                state_machine.process_line(&line);
            }

            let log_snap = state_machine.snapshot();
            {
                let mut snap = state_clone.current_snapshot.write().unwrap();
                snap.log_state = log_snap;
            }

            // Broadcast the snapshot event with updated log state
            let snapshot_event = SseEvent::Snapshot(state_clone.get_snapshot());
            // Suppress errors when there are no subscribers to avoid spam in logs
            let _ = state_clone.broadcaster.send(snapshot_event);

            sleep(Duration::from_secs(2)).await;
        }
    });

    // 30-second heartbeat loop
    let state_clone = Arc::clone(&state);
    tokio::spawn(async move {
        loop {
            let heartbeat_event = SseEvent::Heartbeat(chrono::Utc::now().timestamp());
            // Suppress errors when there are no subscribers to avoid spam in logs
            let _ = state_clone.broadcaster.send(heartbeat_event);
            
            sleep(Duration::from_secs(30)).await;
        }
    });
}
