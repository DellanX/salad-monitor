use salad_monitord::state::{AppState, Capabilities, MetricSample};

#[test]
fn test_app_state_ring_buffer() {
    let caps = Capabilities::default();
    let state = AppState::new(caps);

    for i in 0..400 {
        state.push_sample(MetricSample {
            timestamp_secs: i as i64,
            cpu_usage_pct: (i % 100) as f32,
            memory_usage_pct: 50.0,
            gpu_usage_pct: Some(75),
            gpu_temp_c: Some(65),
            power_w: Some(150.0),
        });
    }

    let snap = state.get_snapshot();
    // Ring buffer capacity capped at 360 items
    assert_eq!(snap.history.len(), 360);
    assert_eq!(snap.history.first().unwrap().timestamp_secs, 40);
    assert_eq!(snap.history.last().unwrap().timestamp_secs, 399);
}
