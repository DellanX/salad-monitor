# Manual Testing Guide

This guide covers manual testing of the Salad Monitor service locally and in Docker.

For information about unit tests and test structure, see [TESTING.md](TESTING.md).

---

## Prerequisites

- Development environment set up (devcontainer or local Python 3.9+)
- Dependencies installed: `pip install -r requirements.txt`

---

## 1. Local Development Testing

### Start the Service

```bash
python salad_monitor.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test Legacy API (Backward Compatibility)

```bash
# Health check
curl http://localhost:8000/health | jq

# GPU status
curl http://localhost:8000/gpu-status | jq

# Version
curl http://localhost:8000/version | jq
```

### Test New v1 API Endpoints

#### Comprehensive Health
```bash
curl http://localhost:8000/api/v1/health | jq
```

#### Wallet Information
```bash
curl http://localhost:8000/api/v1/wallet | jq
```

#### Job Details
```bash
curl http://localhost:8000/api/v1/job | jq
```

#### Download Progress
```bash
curl http://localhost:8000/api/v1/download | jq
```

#### Hardware Metrics
```bash
curl http://localhost:8000/api/v1/hardware | jq
```

#### Network Statistics
```bash
curl http://localhost:8000/api/v1/network | jq
```

#### WSL Status
```bash
curl http://localhost:8000/api/v1/wsl | jq
```

#### GPU Demand Data
```bash
curl http://localhost:8000/api/v1/gpu-demand | jq
```

#### Process Information
```bash
curl http://localhost:8000/api/v1/processes | jq
```

#### Error Tracking
```bash
curl http://localhost:8000/api/v1/errors | jq
```

---

## 2. Debug Mode Testing

Enable debug output to see detailed monitoring activity:

```bash
DEBUG=true python salad_monitor.py
```

Watch console for debug output showing:
- Log parsing events
- Hardware metric updates
- Network bandwidth updates
- GPU demand API calls

---

## 3. Feature Toggle Testing

### Disable Hardware Monitoring
```bash
ENABLE_HARDWARE_MONITORING=false python salad_monitor.py
```

Check `/api/v1/hardware` - should return null/empty values for CPU, RAM, GPU, Disk.

### Disable GPU Demand API
```bash
ENABLE_GPU_DEMAND_API=false python salad_monitor.py
```

Check `/api/v1/gpu-demand` - should return null values.

### Disable Network Monitoring
```bash
ENABLE_NETWORK_MONITORING=false python salad_monitor.py
```

Check `/api/v1/network` - should return null values for bandwidth stats.

### Disable Process Monitoring
```bash
ENABLE_PROCESS_MONITORING=false python salad_monitor.py
```

Check `/api/v1/processes` - should return null values for Salad/Bowl versions.

---

## 4. Log Directory Testing

If you have Salad logs available:

```bash
# Point to actual Salad logs directory
LOG_DIR=/path/to/salad/logs python salad_monitor.py
```

Or on Windows:
```bash
LOG_DIR=C:\ProgramData\Salad\logs python salad_monitor.py
```

Watch for:
- Log file detection
- Wallet updates
- Job ID detection
- Download progress tracking
- Container status changes

---

## 5. API Documentation Testing

Open browser and navigate to:
```
http://localhost:8000/docs
```

You should see the interactive Swagger UI with all endpoints available for testing.

Alternative (ReDoc):
```
http://localhost:8000/redoc
```

---

## 6. Docker Testing

### Build Docker Image
```bash
docker build -t salad-monitor:test .
```

### Run Docker Container
```bash
docker run -d \
  --name salad-monitor-test \
  -p 8000:8000 \
  -v /path/to/salad/logs:/logs \
  -e DEBUG=true \
  salad-monitor:test
```

### Check Container Logs
```bash
docker logs -f salad-monitor-test
```

### Test Endpoints (same as above)
```bash
curl http://localhost:8000/api/v1/health | jq
```

### Stop and Remove Container
```bash
docker stop salad-monitor-test
docker rm salad-monitor-test
```

---

## 7. Load Testing (Optional)

Install load testing tool:
```bash
# macOS
brew install hey

# Linux (from source)
go install github.com/rakyll/hey@latest
```

Run load test:
```bash
# 1000 requests, 10 concurrent connections
hey -n 1000 -c 10 http://localhost:8000/api/v1/health
```

---

## Expected Results

### With No Salad Logs Available

| Field | Expected Value |
|-------|----------------|
| `wallet_balance` | `null` |
| `wallet_projected` | `null` |
| `job_id` | `null` |
| `container_status` | `"Pending..."` |
| `download_progress_pct` | `null` or `0` |
| Hardware metrics | Real values (if psutil available) |
| Network stats | Real values (if psutil available) |
| Process info | Real values (if Salad running) |

### With Salad Logs Available

| Field | Expected Value |
|-------|----------------|
| `wallet_balance` | `"$X.XX"` |
| `wallet_projected` | `"$Y.YY"` |
| `job_id` | UUID string (e.g., `"abc123-def456"`) |
| `container_status` | `"Running (Stable)"` or download info |
| `download_progress_pct` | `0-100` when downloading |
| All other metrics | Populated with real data |

### Hardware Metrics (if dependencies installed)

| Field | Expected Value |
|-------|----------------|
| `cpu_load_pct` | `0-100` |
| `ram_used_gb` | `> 0` |
| `ram_total_gb` | `> 0` |
| `gpu_utilization_pct` | `0-100` (if nvidia-smi available) |
| `gpu_power_watts` | `> 0` (if nvidia-smi available) |
| `gpu_temperature_c` | `> 0` (if nvidia-smi available) |

### GPU Demand API (if requests installed)

| Field | Expected Value |
|-------|----------------|
| `gpu_demand_tier` | Tier name (e.g., `"High Demand"`) or `"API Error"` |
| `gpu_earning_avg_24h` | Dollar amount (e.g., `2.45`) or `null` |
| `gpu_earning_max_24h` | Dollar amount (e.g., `3.50`) or `null` |

---

## Troubleshooting

### Import Errors
**Symptom:**
```
ModuleNotFoundError: No module named 'psutil'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### GPU Not Detected
**Symptom:**
```json
{
  "gpu_name": null,
  "gpu_utilization_pct": null
}
```

**Check:**
- Is `nvidia-smi` available? Run: `nvidia-smi --version`
- Are you running on a system with NVIDIA GPU?
- Is the NVIDIA driver installed?

### No Log Files Found
**Symptom:**
```
[DEBUG] No log files found. Sleeping...
```

**Check:**
- Is `LOG_DIR` environment variable set correctly?
- Does the directory exist and contain `log-*.txt` files?
- On Windows: Use backslashes or raw strings for paths

### GPU Demand API Error
**Symptom:**
```json
{
  "gpu_demand_tier": "API Offline or Error"
}
```

**Check:**
- Internet connection available?
- Salad API status: `curl https://app-api.salad.com/api/v2/demand-monitor/gpu`
- Firewall not blocking outbound HTTPS?

### WSL Not Detected
**Symptom:**
```json
{
  "wsl_status": null,
  "wsl_ram_mb": null
}
```

**Check:**
- Running on Windows?
- WSL installed and running?
- Run: `wsl.exe -l -v` to check WSL status

---

## Success Criteria

Before considering testing complete, verify:

- ✅ Service starts without errors
- ✅ Legacy endpoints return valid JSON
- ✅ All v1 endpoints return valid JSON
- ✅ Hardware metrics populated (if supported)
- ✅ No Python exceptions in logs
- ✅ Feature toggles work correctly
- ✅ API docs accessible at `/docs`
- ✅ Docker container builds successfully
- ✅ Docker container runs without errors

---

## Next Steps After Testing

1. ✅ All tests pass
2. ✅ No errors in logs
3. ✅ API responses match expectations
4. Build production Docker image
5. Push to GitHub Container Registry
6. Update Home Assistant integration
7. Deploy to production
8. Monitor for issues

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [README.md](README.md) for configuration options
2. Enable `DEBUG=true` for detailed logging
3. Check Docker logs: `docker logs salad-monitor`
4. Open an issue on GitHub with:
   - Error messages
   - Configuration used
   - Expected vs actual behavior
