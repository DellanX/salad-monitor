# 🥗 Salad Monitor v1.0

A lightweight, single-binary monitoring daemon and real-time Vue 3 web interface for [Salad Bowl](https://salad.com) node operators.

> **BREAKING CHANGE (v1.0)**: Salad Monitor has been completely rewritten from Python/FastAPI into a high-performance Rust daemon (`salad-monitord`) with an embedded Vue 3 SPA web UI. The separate Windows sidecar process is no longer required.

---

## ✨ Features

- **Single Binary**: Zero runtime dependencies. Web UI, HTTP REST API, SSE streaming server, SQLite webhook database, and hardware collectors bundled into one `.exe`.
- **Real-Time Telemetry**: Instant 1-second metric updates via Server-Sent Events (SSE).
- **Log-Parsed Container State**: Container workload IDs, download ETA, wallet balance, and WSL disk usage parsed directly from Salad log files.
- **NVIDIA GPU Monitoring**: Direct NVML hardware monitoring (utilization, VRAM, temp, power, fan speed, clock speeds, and per-PID process classification) without spawning external subprocesses.
- **mDNS Autodiscovery**: Service autodiscovery (`_salad-monitor._tcp.local.`) across multi-node setups without host daemons.
- **Signed Webhooks**: HMAC-SHA256 signed event notifications with automatic exponential backoff retries.
- **Docker Desktop Ready**: Deployable as a native Windows application or as a Docker container.

---

## 🚀 Quick Start

### Windows Native (.exe)

1. Download `salad-monitord.exe` from [Releases](https://github.com/dellanx/salad-monitor/releases).
2. Run `salad-monitord.exe`.
3. Open `http://localhost:8765` in your browser.

### Docker Compose

```yaml
version: '3.8'
services:
  salad-monitor:
    image: salad-monitor:latest
    ports:
      - "8765:8765"
    volumes:
      - type: bind
        source: C:\ProgramData\Salad\logs
        target: /app/logs
        read_only: true
    environment:
      - NVIDIA_DRIVER_CAPABILITIES=utility,compute
```

```bash
docker compose up -d
```

## 🛠️ Development Setup with GPU Access

To enable GPU access in the devcontainer for testing NVML functionality on Windows with WSL2:

1. Ensure Docker Desktop is running with WSL2 backend
2. Enable GPU support in Docker Desktop Settings:
   - Go to Settings → Resources → WSL Integration
   - Enable integration for your WSL2 distribution
   - Ensure "GPU Support" is enabled in Settings → Resources → GPU
3. Rebuild the devcontainer:
   ```bash
   # In VS Code, run: 
   # Dev Containers: Rebuild Container
   # Or from terminal:
   docker-compose build --no-cache
   docker-compose up -d
   ```
4. Verify GPU access by running tests or using the test script in the repository root: `test_gpu_access.rs`

---

## 🛠️ Architecture Overview

```
                      +---------------------------------------+
                      |         salad-monitord (Rust)         |
                      |                                       |
                      |  +---------------------------------+  |
                      |  |      Axum Web & SSE Server      |  |
                      |  +---------------------------------+  |
                      |  |   Embedded Vue 3 SPA (rust-embed)|  |
                      |  +---------------------------------+  |
                      |  | Collectors: nvml / sysinfo / logs|  |
                      +--+---------------------------------+--+
                                         |
                                         v
                         http://localhost:8765 (Dashboard)
```

For complete technical specifications, see:
- [Architecture & ADRs](docs/architecture.md)
- [SaladXRay Feature Parity Matrix](docs/parity.md)
- [API Contract](docs/api.md)
- [Security Model](docs/security.md)
- [Deployment Guide](docs/deployment.md)

---

## ⚠️ Hardware Compatibility Notice

- **NVIDIA GPUs**: Full support via `nvml-wrapper` 0.13.
- **AMD GPUs**: Unsupported in v1.0 due to OS-specific crate limitations on Windows native. Non-NVIDIA systems operate cleanly with GPU metrics gracefully disabled.
- **Intel GPUs**: Unsupported.

    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - C:\ProgramData\Salad\logs:/logs
    environment:
      - DEBUG=false
      - ENABLE_HARDWARE_MONITORING=true
      - ENABLE_GPU_DEMAND_API=true
      - ENABLE_NETWORK_MONITORING=true
      - ENABLE_PROCESS_MONITORING=true
      - COLLECTOR_MODE=sidecar_push
      - SIDECAR_AUTH_TOKEN=change-me
```

---

## 🪟 Native Windows EXE

You can build both executables (main monitor + optional sidecar):

```powershell
pip install -r requirements.txt
pip install -r requirements-build.txt
.\scripts\build-windows.ps1 -Version 0.2.0
```

Output:
- `dist\salad-monitor.exe`
- `dist\salad-sidecar.exe`

### Run as Windows services

Use NSSM to install either executable:

```powershell
.\scripts\install-salad-monitor-service.ps1 -NssmPath C:\tools\nssm\nssm.exe
.\scripts\install-salad-sidecar-service.ps1 -NssmPath C:\tools\nssm\nssm.exe
```

### Sign artifacts

```powershell
.\scripts\sign-artifacts.ps1 -CertificateThumbprint <thumbprint>
```

> Sidecar is optional for native EXE installs. It is intended for Docker deployments where host metrics must be pushed into the container.

Common sidecar target overrides:
- `SIDECAR_TARGET_URL` (full URL override)
- or granular values:
  - `SIDECAR_TARGET_SCHEME` (default `http`)
  - `SIDECAR_TARGET_HOST` (default `127.0.0.1`)
  - `SIDECAR_TARGET_PORT` (default `8000`)
  - `SIDECAR_TARGET_PATH` (default `/api/v1/sidecar/report`)

### Sidecar authentication kickoff

Sidecar auth is a shared-token flow (no interactive login):

1. Set the container to sidecar mode with a token:
   - `COLLECTOR_MODE=sidecar_push`
   - `SIDECAR_AUTH_TOKEN=<long-random-token>`
2. Start/restart Salad Monitor container.
3. Set the same token on the Windows sidecar:
   - `SIDECAR_AUTH_TOKEN=<same-token>`
   - optional target override: `SIDECAR_TARGET_HOST`, `SIDECAR_TARGET_PORT`
4. Start sidecar process/service.
5. Verify:
   - `GET /api/v1/collector`
   - check `sidecar.last_seen`, `sidecar.stale=false`, and `sidecar.update_required`.

If token mismatches, the sidecar gets `401` on `POST /api/v1/sidecar/report`.
Sidecar compatibility is paired to the monitor build version (`minimum_supported_version` in collector status).

---

## 📡 API Endpoints

### Legacy API (Backward Compatible)
- `GET /health` - Overall health and status information
- `GET /gpu-status` - Current GPU and workload status
- `GET /version` - Application version
- `GET /current-logfile` - Current logfile path
- `GET /current-logfile-contents?lines=N` - Logfile contents (last N lines)
- `GET /logs` - List all available log files
- `GET /tail?lines=N` - Tail current logfile (last N lines)
- `GET /debug` - Debug mode status

### New v1 API (Enhanced Features)

#### Comprehensive Data
- `GET /api/v1/health` - Complete health with all enhanced metrics
- `GET /api/v1/collector` - Collector mode, runtime settings, and sidecar status
- `POST /api/v1/sidecar/report` - Sidecar payload ingest (only when `COLLECTOR_MODE=sidecar_push`)

#### Wallet & Earnings
- `GET /api/v1/wallet` - Wallet balance and projected earnings
```json
{
  "balance": "$1.23",
  "projected": "$2.45",
  "last_update": "2024-01-15T10:30:00"
}
```

#### Job Information
- `GET /api/v1/job` - Current job details and uptime
```json
{
  "job_id": "abc123-def456",
  "start_time": "2024-01-15T09:00:00",
  "uptime_seconds": 5400,
  "container_status": "Running (Stable)",
  "matrix_status": "Job Acquired! (1 active workload)"
}
```

#### Download Progress
- `GET /api/v1/download` - Container download status
```json
{
  "is_downloading": true,
  "progress_pct": 45.2,
  "active_layer": "a1b2c3d4",
  "speed_kbps": 2048.5,
  "estimated_mb": 1024.0,
  "eta_seconds": 300
}
```

#### Hardware Metrics
- `GET /api/v1/hardware` - CPU, RAM, GPU, Disk metrics
```json
{
  "cpu": {
    "name": "AMD Ryzen 9 5900X",
    "load_pct": 35.2
  },
  "ram": {
    "used_gb": 12.5,
    "total_gb": 32.0,
    "load_pct": 39.1
  },
  "gpu": {
    "name": "RTX 3080",
    "utilization_pct": 98.5,
    "power_watts": 320.5,
    "temperature_c": 72.0
  },
  "disk": {
    "type": "NVMe SSD",
    "size_gb": 1000,
    "utilization_pct": 45.3
  }
}
```

#### Network Statistics
- `GET /api/v1/network` - WSL and SGS bandwidth usage
```json
{
  "wsl": {
    "rx_kbps": 2048.5,
    "tx_kbps": 512.3,
    "total_rx_gb": 15.23,
    "total_tx_gb": 2.45
  },
  "sgs": {
    "rx_kbps": 100.2,
    "tx_kbps": 50.1,
    "total_rx_mb": 500.5,
    "total_tx_mb": 250.2,
    "ram_mb": 128.5
  },
  "bandwidth": {
    "active": true,
    "node_name": "Bandwidth-xyz123"
  }
}
```

#### GPU Demand (from Salad API)
- `GET /api/v1/gpu-demand` - Market demand and earning rates
```json
{
  "tier": "High Demand",
  "utilization_pct": 85.5,
  "earning_avg_24h": 2.45,
  "earning_max_24h": 3.50,
  "recommended_ram_gb": 16,
  "last_update": "2024-01-15T10:25:00"
}
```

#### Process Information
- `GET /api/v1/processes` - Salad processes and miner detection
```json
{
  "salad": {
    "version": "1.2.3",
    "uptime_seconds": 86400
  },
  "salad_bowl": {
    "version": "2.3.4",
    "uptime_seconds": 86400
  },
  "miner": {
    "active": true,
    "name": "t-rex"
  }
}
```

#### WSL Status
- `GET /api/v1/wsl` - WSL resource usage
```json
{
  "status": "Running",
  "ram_mb": 2048.5,
  "disk_size_gb": 25.3
}
```

#### Error Tracking
- `GET /api/v1/errors` - Last warning/error
```json
{
  "last_warning": "Network timeout detected",
  "last_warning_time": "2024-01-15T10:20:00"
}
```

#### Log Files
- `GET /api/v1/logs` - List all log files
- `GET /api/v1/current-logfile` - Current logfile path
- `GET /api/v1/current-logfile-contents?lines=N` - Logfile contents
- `GET /api/v1/tail?lines=N` - Tail current logfile
- `GET /api/v1/version` - Application version

---

## 🏠 Home Assistant Integration

https://github.com/dellanx/salad-monitor-ha

The Home Assistant integration provides sensors for all the enhanced metrics including wallet balance, job status, download progress, hardware metrics, and more.

---

## 🔧 Development

### Prerequisites
- Python 3.9+
- pip

### Setup
```bash
git clone https://github.com/dellanx/salad-monitor.git
cd salad-monitor
pip install -r requirements.txt
```

### Run locally
```bash
python salad_monitor.py
```

### Run tests
```bash
pytest
```

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

Inspired by [SaladXRay](https://github.com/joseluisfreire/SaladXRay) - a comprehensive Windows monitoring tool for Salad nodes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 🧪 Development & Testing

### Development Environment

This project uses a devcontainer for development. To get started:

1. Install Docker and VS Code with the Remote-Containers extension
2. Open the project in VS Code
3. Click "Reopen in Container" when prompted
4. Dependencies will be automatically installed

### Running Tests

The project uses pytest for testing. The test directory structure mirrors the source code structure.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_config.py
```

For detailed testing documentation, see [TESTING.md](TESTING.md).

### Project Structure

```
salad-monitor/
├── src/                 # Source code
│   ├── api/            # API routes
│   ├── config.py       # Configuration
│   ├── state.py        # State management
│   ├── log_parser.py   # Log parsing logic
│   └── ...
├── tests/              # Tests (mirrors src/ structure)
│   ├── api/
│   ├── test_config.py
│   ├── test_state.py
│   └── ...
├── .devcontainer/      # Development container config
└── requirements.txt    # Python dependencies
```
