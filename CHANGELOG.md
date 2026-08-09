# Changelog

All notable changes to the Salad Monitor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-08-08

### 🎉 Major Update: Enhanced Monitoring Capabilities

This release adds comprehensive monitoring capabilities inspired by [SaladXRay](https://github.com/joseluisfreire/SaladXRay), transforming Salad Monitor from a basic log parser into a full-featured monitoring service.

### Added

#### New API Endpoints (`/api/v1` prefix)
- `/api/v1/health` - Comprehensive health check with all metrics
- `/api/v1/wallet` - Wallet balance and projected earnings
- `/api/v1/job` - Job details, uptime, and container status
- `/api/v1/download` - Container download progress with ETA
- `/api/v1/hardware` - CPU, RAM, GPU, and disk metrics
- `/api/v1/network` - WSL and SGS bandwidth statistics
- `/api/v1/wsl` - WSL status and resource usage
- `/api/v1/gpu-demand` - GPU demand data from Salad's public API
- `/api/v1/processes` - Salad process versions and miner detection
- `/api/v1/errors` - Error and warning tracking

#### New Monitoring Modules
- `src/hardware.py` - Hardware monitoring (GPU, CPU, RAM, Disk)
- `src/network.py` - Network bandwidth tracking (WSL, SGS processes)
- `src/gpu_demand.py` - GPU demand API client with caching
- `src/processes.py` - Process detection and version extraction

#### Enhanced Log Parsing
- Wallet information extraction (`Wallet: Current(...), Predicted(...)`)
- Job ID tracking and uptime calculation
- Download progress with speed and ETA calculation
- Matrix status detection
- Container status detection (Running, Stopped, Downloading)
- Bandwidth node detection
- WSL disk size extraction
- Error and warning tracking

#### Configuration Options
- `ENABLE_HARDWARE_MONITORING` - Toggle hardware monitoring (default: `true`)
- `ENABLE_GPU_DEMAND_API` - Toggle GPU demand API (default: `true`)
- `ENABLE_NETWORK_MONITORING` - Toggle network monitoring (default: `true`)
- `ENABLE_PROCESS_MONITORING` - Toggle process monitoring (default: `true`)
- `GPU_DEMAND_CACHE_MINUTES` - GPU demand cache duration (default: `5`)

#### Dependencies
- `psutil>=5.9.0` - System and process utilities
- `requests>=2.31.0` - HTTP client for GPU demand API

#### Documentation
- Comprehensive [README.md](README.md) with all API endpoints documented
- [MANUAL_TESTING.md](MANUAL_TESTING.md) - Manual testing procedures
- Updated [TESTING.md](TESTING.md) - Unit test structure reference

### Changed

#### State Management
- Expanded state dict from 5 fields to 60+ fields
- Added helper functions for state updates
- Added datetime serialization for API responses

#### Monitoring Loop
- Enhanced monitor loop to call all monitoring modules
- Added 2-second polling interval for hardware/network updates
- Added graceful error handling for each monitoring module

#### API Application
- Updated FastAPI app to include both legacy and v1 routers
- Version bumped to 0.2.0

### Maintained

#### Backward Compatibility
- All legacy API endpoints preserved (`/health`, `/gpu-status`, `/version`, etc.)
- Original state fields unchanged
- No breaking changes to existing integrations

### Technical Details

#### Files Created
- `src/api/routes_v1.py` - New v1 API router
- `src/hardware.py` - Hardware monitoring module
- `src/network.py` - Network monitoring module
- `src/gpu_demand.py` - GPU demand API client
- `src/processes.py` - Process detection module
- `MANUAL_TESTING.md` - Manual testing guide
- `CHANGELOG.md` - This file

#### Files Modified
- `src/state.py` - Expanded state with 60+ new fields
- `src/log_parser.py` - Enhanced with 10+ new parsing patterns
- `src/monitor.py` - Integrated all new monitoring modules
- `src/config.py` - Added feature toggle configuration
- `src/app.py` - Included v1 router
- `requirements.txt` - Added psutil and requests
- `README.md` - Comprehensive documentation update
- `TESTING.md` - Added manual testing reference

#### Code Statistics
- **1,548 lines** of Python code in `src/`
- **5 new modules** (hardware, network, gpu_demand, processes, routes_v1)
- **60+ state fields** for comprehensive monitoring
- **10+ log parsing patterns** from SaladXRay

### Comparison with SaladXRay

This release achieves feature parity with SaladXRay while adding:
- ✅ REST API (SaladXRay is console-only)
- ✅ Docker support
- ✅ Home Assistant integration
- ✅ Cross-platform support (Linux/Windows)
- ✅ Configurable feature toggles

---

## [0.1.x] - Previous Releases

### Initial Pre-Release

#### Features
- Basic Salad log parsing
- Workload state detection (pending, active, GPU reserved)
- Simple REST API endpoints:
  - `/health`
  - `/gpu-status`
  - `/version`
  - `/current-logfile`
  - `/logs`
  - `/tail`
  - `/debug`
- Docker support
- Home Assistant integration

---

---

## Roadmap to 1.0.0

### Before 1.0 Release
- [ ] Complete unit test coverage
- [ ] Production testing with real Salad logs
- [ ] Performance optimization
- [ ] Security review
- [ ] Documentation review

### Planned for Future Releases
- [ ] WebSocket support for real-time updates
- [ ] Historical data storage (SQLite/Redis)
- [ ] Metrics export (Prometheus format)
- [ ] Alerting system for errors/warnings
- [ ] Performance profiling
- [ ] Extended unit test coverage

### Under Consideration
- [ ] Web UI dashboard
- [ ] Multi-node monitoring
- [ ] Custom alert rules
- [ ] Data export capabilities

---

## Links

- [GitHub Repository](https://github.com/dellanx/salad-monitor)
- [Docker Image](https://ghcr.io/dellanx/salad-monitor)
- [Home Assistant Integration](https://github.com/dellanx/salad-monitor-ha)
- [SaladXRay (Inspiration)](https://github.com/joseluisfreire/SaladXRay)
