//! mDNS autodiscovery service registration via `mdns-sd`.
//!
//! Service type: `_salad-monitor._tcp.local.`
//! Operates cleanly in multi-instance environments and handles container/WSL2 network limitations gracefully.

use mdns_sd::{ServiceDaemon, ServiceInfo};
use std::collections::HashMap;

pub struct MdnsDiscoveryService {
    daemon: Option<ServiceDaemon>,
    fullname: Option<String>,
}

impl MdnsDiscoveryService {
    pub fn new() -> Self {
        Self {
            daemon: None,
            fullname: None,
        }
    }

    /// Registers the salad-monitor mDNS service.
    pub fn register(&mut self, port: u16, instance_name: &str, capabilities_summary: &str) {
        let daemon = match ServiceDaemon::new() {
            Ok(d) => d,
            Err(e) => {
                eprintln!("mDNS daemon creation failed (non-fatal): {}", e);
                return;
            }
        };

        let service_type = "_salad-monitor._tcp.local.";
        let host_name = format!("{}.local.", instance_name.replace(' ', "-"));
        let mut txt_records = HashMap::new();
        txt_records.insert("version".to_string(), "1.0.0".to_string());
        txt_records.insert("capabilities".to_string(), capabilities_summary.to_string());
        txt_records.insert("port".to_string(), port.to_string());

        let service_info = match ServiceInfo::new(
            service_type,
            instance_name,
            &host_name,
            "",
            port,
            txt_records,
        ) {
            Ok(info) => info,
            Err(e) => {
                eprintln!("Failed to create mDNS ServiceInfo: {}", e);
                return;
            }
        };

        let fullname = service_info.get_fullname().to_string();
        if let Err(e) = daemon.register(service_info) {
            eprintln!("Failed to register mDNS service: {}", e);
            return;
        }

        self.daemon = Some(daemon);
        self.fullname = Some(fullname);
        println!("Registered mDNS service: {} on port {}", instance_name, port);
    }

    /// Unregisters the service on shutdown.
    pub fn unregister(&mut self) {
        if let (Some(daemon), Some(fullname)) = (&self.daemon, &self.fullname) {
            let _ = daemon.unregister(fullname);
        }
        self.daemon = None;
        self.fullname = None;
    }
}

impl Drop for MdnsDiscoveryService {
    fn drop(&mut self) {
        self.unregister();
    }
}
