//! Binary entrypoint for the salad-monitord daemon.

pub mod api;
pub mod auth;
pub mod embed;
pub mod mdns;
pub mod scheduler;
pub mod state;

use api::create_router;
use mdns::MdnsDiscoveryService;
use scheduler::start_scheduler;
use salad_collect::nvml_collector::NvmlCollector;
use state::{AppState, Capabilities};
use std::net::SocketAddr;
use std::path::PathBuf;
use sysinfo::System;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Starting Salad Monitor Daemon v1.0.0...");

    let mut capabilities = Capabilities::default();
    capabilities.gpu_nvidia = NvmlCollector::is_available();

    let state = AppState::new(capabilities);

    // Start the scheduler to collect telemetry
    let log_dir = PathBuf::from("/app/logs");
    start_scheduler(state.clone(), log_dir);

    // Register mDNS autodiscovery
    let mut mdns = MdnsDiscoveryService::new();
    let hostname = System::host_name().unwrap_or_else(|| "SaladNode".to_string());
    mdns.register(8765, &format!("SaladMonitor-{}", hostname), "v1.0.0");

    let app = create_router(state);
    let addr = SocketAddr::from(([0, 0, 0, 0], 8765));
    println!("Salad Monitor HTTP & SSE server listening on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

