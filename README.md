# 🥗 Salad Monitor

A comprehensive FastAPI service that monitors your Salad GPU workload with enhanced metrics and exposes clean REST APIs for Home Assistant or other automation systems.

This service watches your Salad logs, tracks GPU activity, workload state, hardware metrics, network statistics, and provides detailed JSON APIs for external systems.

---

## 🚀 Features

### Core Monitoring
- Real‑time monitoring of Salad GPU activity
- Parses Salad log files for:
  - Active workload state
  - Pending workload state
  - GPU reservation state
  - Last event and current logfile

### Enhanced Metrics (v2.0+)
- **💰 Wallet Information**: Balance, projected earnings, last update time
- **📦 Job Tracking**: Job ID, uptime, container status, matrix connection
- **⬇️ Download Progress**: Real-time progress %, speed, ETA for container downloads
- **🌐 GPU Demand Data**: Market demand, earning rates from Salad's public API
- **🖥️ Hardware Metrics**: CPU/RAM/GPU utilization, temperature, power draw
- **📊 Network Stats**: Real-time bandwidth usage (WSL and SGS processes)
- **⚙️ Process Info**: Salad/Bowl Service versions, uptime, miner detection
- **🐧 WSL Monitoring**: Status and resource usage
- **⚠️ Error Tracking**: Last warnings/errors from logs

### API
- Clean REST API with both legacy and `/api/v1` endpoints
- Lightweight FastAPI server
- Docker‑ready
- Works seamlessly with the **Salad Monitor Home Assistant Integration**

---

## 📦 Installation

You can run Salad Monitor:

- As a Docker container
- In Portainer
- Directly via Python
- As a systemd service

Below are the recommended installation methods.

---

## 🐳 Docker Installation (Recommended)

The official image is published to GitHub Container Registry:

ghcr.io/dellanx/salad-monitor:latest

### Run with Docker CLI

```bash
docker run -d \
  --name salad-monitor \
  -p 8000:8000 \
  -v C:\ProgramData\Salad\logs:/logs \
  ghcr.io/dellanx/salad-monitor:latest
```

### Required volume

| Host Path                   | Container Path | Purpose                      |
| --------------------------- | -------------- | ---------------------------- |
| `C:\ProgramData\Salad\logs` | `/logs`        | Folder containing Salad logs |

### Environment Variables

| Variable                       | Description                                  | Default |
| ------------------------------ | -------------------------------------------- | ------- |
| `LOG_DIR`                      | Path to Salad logs inside container         | `/logs` |
| `PORT`                         | API port                                     | `8000`  |
| `DEBUG`                        | Enable debug mode                            | `false` |
| `ENABLE_HARDWARE_MONITORING`   | Enable CPU/RAM/GPU/Disk monitoring           | `true`  |
| `ENABLE_GPU_DEMAND_API`        | Enable GPU demand data from Salad API        | `true`  |
| `ENABLE_NETWORK_MONITORING`    | Enable network bandwidth tracking            | `true`  |
| `ENABLE_PROCESS_MONITORING`    | Enable Salad process and miner detection     | `true`  |
| `GPU_DEMAND_CACHE_MINUTES`     | Cache duration for GPU demand API (minutes)  | `5`     |

## Docker Compose Example

```docker-compose
version: "3.9"

services:
  salad-monitor:
    image: ghcr.io/dellanx/salad-monitor:latest
    container_name: salad-monitor
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
```

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
