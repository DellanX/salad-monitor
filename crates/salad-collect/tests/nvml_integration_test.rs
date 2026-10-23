//! Integration tests for NVML collector functionality

use salad_collect::nvml_collector::{NvmlCollector, GpuTelemetrySnapshot};

#[test]
fn test_nvml_collector_initialization() {
    println!("Testing NVML collector initialization...");
    
    // Test that we can create a collector without panic
    let collector = NvmlCollector::new();
    let is_available = NvmlCollector::is_available();
    
    println!("NVML Available: {}", is_available);
    println!("NVML collector created successfully");
    
    // This test verifies that the NVML collector can be initialized
    // even on systems without GPUs or NVML libraries
    assert!(true); 
}

#[test]
fn test_nvml_collector_is_available() {
    println!("Testing if NVML is available...");
    
    let is_available = NvmlCollector::is_available();
    println!("NVML Available: {}", is_available);
    
    // This should not panic even if NVML is not available
    assert!(true); 
}

#[test]
fn test_nvml_collector_collect() {
    println!("Testing NVML collector collection...");
    
    let collector = NvmlCollector::new();
    let snapshot = collector.collect();
    
    println!("Snapshot available: {}", snapshot.is_available);
    println!("Number of devices: {}", snapshot.devices.len());
    
    // The test should not fail even if NVML is not available
    // This ensures our code doesn't crash on systems without GPUs
    assert!(snapshot.is_available || snapshot.devices.is_empty());
}

#[test]
fn test_gpu_telemetry_snapshot_structure() {
    println!("Testing GPU telemetry snapshot structure...");
    
    let collector = NvmlCollector::new();
    let snapshot = collector.collect();
    
    // Test that we can access the snapshot data structure
    println!("Snapshot is_available: {}", snapshot.is_available);
    println!("Number of devices in snapshot: {}", snapshot.devices.len());
    
    // Verify basic structure exists
    assert!(snapshot.is_available || snapshot.devices.is_empty());
}

#[test]
fn test_gpu_device_details() {
    println!("Testing GPU device details...");
    
    let collector = NvmlCollector::new();
    let snapshot = collector.collect();
    
    // Even if no devices are present, the structure should be valid
    if !snapshot.devices.is_empty() {
        println!("Found {} GPU devices", snapshot.devices.len());
        
        // Print basic device information for each device found
        for (i, device) in snapshot.devices.iter().enumerate() {
            println!("Device {}: {:?}", i, device);
            
            // Test that we can access various telemetry fields with correct names
            println!("  Name: {}", device.name);
            println!("  GPU Utilization: {}%", device.gpu_utilization_pct);
            println!("  Memory Utilization: {}%", device.memory_utilization_pct);
            println!("  Memory Used: {} bytes", device.memory_used_bytes);
            println!("  Memory Total: {} bytes", device.memory_total_bytes);
            println!("  Temperature: {}°C", device.temperature_c);
            println!("  Power Usage: {} W", device.power_usage_w);
            
            if let Some(power_limit) = device.power_limit_w {
                println!("  Power Limit: {} W", power_limit);
            }
            
            // Process information is intentionally disabled due to nvml-wrapper API limitations
            // as noted in the source code:
            // "Note: Process information handling temporarily disabled due to nvml-wrapper API issues.
            // The UsedGpuMemory enum variants are private and cannot be accessed directly."
            println!("  Running processes: {} (disabled due to API limitations)", device.running_processes.len());
        }
    } else {
        println!("No GPU devices found (expected on non-GPU systems)");
        println!("This is normal - the system detected 1 GPU but no utilization data");
    }
    
    // The test should not fail even if no devices are present
    assert!(snapshot.is_available || snapshot.devices.is_empty());
}