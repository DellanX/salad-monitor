# Deployment Guide: Salad Monitor v1.0

`salad-monitor` is distributed as a single standalone executable (`salad-monitord.exe` on Windows, `salad-monitord` on Linux) containing the HTTP/SSE daemon and embedded Vue 3 SPA frontend.

---

## Option 1: Native Windows Executable (.exe)

Running natively on Windows provides **100% full feature parity**, including Windows registry lookups, WMI queries, WSL status, host process tree inspection, and per-PID GPU attribution.

### Quick Start (Interactive)
1. Download `salad-monitord.exe` from the latest release.
2. Double-click `salad-monitord.exe` or execute from PowerShell:
   ```powershell
   .\salad-monitord.exe
   ```
3. Open your browser to `http://localhost:8765`.

### Install as Windows Service
To run `salad-monitord` automatically on boot in the background:
```powershell
# Run PowerShell as Administrator
sc.exe create SaladMonitor binPath= "C:\Path\To\salad-monitord.exe" start= auto
sc.exe start SaladMonitor
```

---

## Option 2: Docker Container (Docker Desktop)

Running inside Docker Desktop is supported with capability degradation.

### Container Environment Requirements
- **NVIDIA GPU Telemetry**: Set `NVIDIA_DRIVER_CAPABILITIES=utility,compute`. The `utility` capability is required to mount `libnvidia-ml.so.1`.
- **Log Parsing**: Bind-mount host log directory `C:\ProgramData\Salad\logs` into `/app/logs` read-only.
- **Per-PID GPU Attribution**: Optional `--pid=host` flag required for NVML to match container PIDs to host processes.

### Running with Docker Compose
```bash
docker compose up -d
```

Access the dashboard at `http://localhost:8765`.
