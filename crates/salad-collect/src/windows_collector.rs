//! Windows-native WMI, registry, and process tree collectors.
//!
//! Only compiled on `cfg(windows)`.

use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WslDistroInfo {
    pub name: String,
    pub state: String,
    pub version: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SaladProcessInfo {
    pub pid: u32,
    pub name: String,
    pub memory_bytes: u64,
    pub is_miner: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WindowsTelemetrySnapshot {
    pub salad_version: Option<String>,
    pub salad_install_path: Option<String>,
    pub wsl_distros: Vec<WslDistroInfo>,
    pub vmmem_ram_bytes: Option<u64>,
    pub salad_processes: Vec<SaladProcessInfo>,
}

pub struct WindowsCollector;

impl WindowsCollector {
    pub fn new() -> Self {
        Self
    }

    pub fn collect(&self) -> WindowsTelemetrySnapshot {
        let salad_version = Self::get_salad_version();
        let salad_install_path = Self::get_salad_install_path();
        let wsl_distros = Self::get_wsl_status();
        let salad_processes = Self::get_salad_processes();

        let vmmem_ram = salad_processes
            .iter()
            .find(|p| p.name.to_lowercase() == "vmmem" || p.name.to_lowercase().starts_with("vmmem"))
            .map(|p| p.memory_bytes);

        WindowsTelemetrySnapshot {
            salad_version,
            salad_install_path,
            wsl_distros,
            vmmem_ram_bytes: vmmem_ram,
            salad_processes,
        }
    }

    fn get_salad_version() -> Option<String> {
        // Try registry lookup for Salad App
        if let Ok(hkcu) = winreg::RegKey::predef(winreg::enums::HKEY_CURRENT_USER)
            .open_subkey("SOFTWARE\\Salad Technologies\\Salad")
        {
            if let Ok(ver) = hkcu.get_value::<String, _>("Version") {
                return Some(ver);
            }
        }
        None
    }

    fn get_salad_install_path() -> Option<String> {
        if let Ok(hkcu) = winreg::RegKey::predef(winreg::enums::HKEY_CURRENT_USER)
            .open_subkey("SOFTWARE\\Salad Technologies\\Salad")
        {
            if let Ok(path) = hkcu.get_value::<String, _>("InstallPath") {
                return Some(path);
            }
        }
        None
    }

    fn get_wsl_status() -> Vec<WslDistroInfo> {
        let mut distros = Vec::new();
        if let Ok(output) = Command::new("wsl.exe").args(["--list", "--verbose"]).output() {
            if output.status.success() {
                let stdout = String::from_utf8_lossy(&output.stdout);
                for line in stdout.lines().skip(1) {
                    let cleaned = line.replace('*', "").trim().to_string();
                    let parts: Vec<&str> = cleaned.split_whitespace().collect();
                    if parts.len() >= 3 {
                        let name = parts[0].to_string();
                        let state = parts[1].to_string();
                        let version = parts[2].parse::<u32>().unwrap_or(2);
                        distros.push(WslDistroInfo { name, state, version });
                    }
                }
            }
        }
        distros
    }

    fn get_salad_processes() -> Vec<SaladProcessInfo> {
        let mut processes = Vec::new();
        let mut sys = sysinfo::System::new();
        sys.refresh_processes(sysinfo::ProcessesToUpdate::All, true);

        for (pid, proc) in sys.processes() {
            let name = proc.name().to_string_lossy().to_string();
            let name_lower = name.to_lowercase();

            let is_salad_related = name_lower.contains("salad")
                || name_lower.contains("vmmem")
                || name_lower.contains("phoenixminer")
                || name_lower.contains("xmrig")
                || name_lower.contains("nbminer")
                || name_lower.contains("gminer")
                || name_lower.contains("trex");

            if is_salad_related {
                let is_miner = !name_lower.contains("salad") && !name_lower.contains("vmmem");
                processes.push(SaladProcessInfo {
                    pid: pid.as_u32(),
                    name,
                    memory_bytes: proc.memory(),
                    is_miner,
                });
            }
        }

        processes
    }
}

