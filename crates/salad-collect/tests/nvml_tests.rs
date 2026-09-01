use salad_collect::nvml_collector::NvmlCollector;

#[test]
fn test_nvml_collector_handles_missing_gpu_gracefully() {
    let collector = NvmlCollector::new();
    let snapshot = collector.collect();

    // On non-NVIDIA test runner systems, is_available should be false and devices empty.
    // The key requirement is that it does NOT panic.
    if !snapshot.is_available {
        assert!(snapshot.devices.is_empty());
    }
}
