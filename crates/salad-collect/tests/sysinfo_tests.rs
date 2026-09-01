use salad_collect::demand_api::{normalize_gpu_name, DemandApiClient, GpuDemandInfo};
use salad_collect::sysinfo_collector::SysinfoCollector;

#[test]
fn test_sysinfo_collection() {
    let mut collector = SysinfoCollector::new();
    let snapshot = collector.collect();

    assert!(snapshot.cpu.core_count > 0);
    assert!(snapshot.memory.total_bytes > 0);
    assert!(!snapshot.system_info.hostname.is_empty());
}

#[test]
fn test_normalize_gpu_name() {
    assert_eq!(normalize_gpu_name("NVIDIA GeForce RTX 3080"), "3080");
    assert_eq!(normalize_gpu_name("NVIDIA RTX 4090 Laptop GPU"), "4090");
    assert_eq!(normalize_gpu_name("GTX 1660 Ti"), "1660 ti");
}

#[test]
fn test_find_matching_demand() {
    let demand_list = vec![
        GpuDemandInfo {
            id: "1".to_string(),
            name: "RTX 3080".to_string(),
            demand_grade: "High".to_string(),
            price_usd_per_hr: 0.25,
        },
        GpuDemandInfo {
            id: "2".to_string(),
            name: "RTX 4090".to_string(),
            demand_grade: "Extreme".to_string(),
            price_usd_per_hr: 0.60,
        },
    ];

    let matched = DemandApiClient::find_matching_demand("NVIDIA GeForce RTX 3080", &demand_list);
    assert!(matched.is_some());
    assert_eq!(matched.unwrap().id, "1");
}
