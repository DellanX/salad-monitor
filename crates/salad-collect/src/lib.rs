//! Hardware, GPU, process, and external API collector implementations.

pub mod sysinfo_collector;
pub mod nvml_collector;
pub mod demand_api;
#[cfg(windows)]
pub mod windows_collector;
