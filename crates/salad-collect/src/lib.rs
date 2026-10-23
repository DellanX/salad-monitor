//! Hardware, GPU, process, and external API collector implementations.

pub mod sysinfo_collector;
pub mod nvml_collector;
pub mod demand_api;
#[cfg(windows)]
pub mod windows_collector;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_gpu_access() {
        // This test will be skipped if NVML is not available
        println!("Testing GPU access...");
        let collector = nvml_collector::NvmlCollector::new();
        let is_available = nvml_collector::NvmlCollector::is_available();
        println!("NVML Available: {}", is_available);
    }
}
