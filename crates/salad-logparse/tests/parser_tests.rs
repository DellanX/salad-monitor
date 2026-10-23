use salad_logparse::parser::{parse_log_line, LogEvent};
use salad_logparse::state_machine::{LogStateMachine, WorkloadStatus};
use std::fs;
use std::path::PathBuf;

#[test]
fn test_parse_wallet() {
    let line = "2026-03-30 12:00:00 [INF] Wallet: Current(12.345), Predicted(0.123)";
    match parse_log_line(line) {
        LogEvent::Wallet { balance, projected } => {
            assert!((balance - 12.345).abs() < 1e-4);
            assert!((projected - 0.123).abs() < 1e-4);
        }
        other => panic!("Expected Wallet event, got {:?}", other),
    }
}

#[test]
fn test_parse_workload_id() {
    let line = "2026-03-30 12:00:01 [INF] Creating container for salad.com/sce/abc-123-def-456";
    match parse_log_line(line) {
        LogEvent::WorkloadId(id) => {
            assert_eq!(id, "abc-123-def-456");
        }
        other => panic!("Expected WorkloadId event, got {:?}", other),
    }
}

#[test]
fn test_parse_global_progress() {
    let line = "2026-03-30 12:00:02 [INF] Progress(0.456)";
    match parse_log_line(line) {
        LogEvent::GlobalProgress(pct) => {
            assert!((pct - 45.6).abs() < 1e-2);
        }
        other => panic!("Expected GlobalProgress event, got {:?}", other),
    }
}

#[test]
fn test_parse_bandwidth_node() {
    let line = "2026-03-30 12:00:03 [INF] Starting workload Bandwidth-Node-01";
    match parse_log_line(line) {
        LogEvent::BandwidthNode(node) => {
            assert_eq!(node, "Bandwidth-Node-01");
        }
        other => panic!("Expected BandwidthNode event, got {:?}", other),
    }
}

#[test]
fn test_state_machine_with_sample_fixture() {
    let mut fixture_path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    fixture_path.pop(); // crates
    fixture_path.pop(); // root
    fixture_path.push("tests");
    fixture_path.push("fixtures");
    fixture_path.push("logs");
    fixture_path.push("sample-salad-log.txt");

    if fixture_path.exists() {
        let content = fs::read_to_string(&fixture_path).expect("Failed to read fixture log");
        let mut state_machine = LogStateMachine::new();

        for line in content.lines() {
            state_machine.process_line(line);
        }

        let snap = state_machine.snapshot();
        assert!((snap.wallet_balance - 12.3456).abs() < 1e-4);
        assert_eq!(snap.workload_id.as_deref(), Some("abc12345-6789-abcd-ef01-234567890abc"));
        assert_eq!(snap.status, WorkloadStatus::Running);
        assert_eq!(snap.bandwidth_node.as_deref(), Some("Bandwidth-US-East-42"));
        assert!((snap.distro_size_gb.unwrap() - 15.0).abs() < 0.1);
    }
}
