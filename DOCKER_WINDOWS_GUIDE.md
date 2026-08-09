# Running Salad Monitor on Docker Desktop for Windows

## API Endpoint for Feature Flags

### Check Feature Flag Status
```bash
curl http://localhost:8000/api/v1/health
```

**Response Example:**
```json
{
  "monitor_running": true,
  "current_logfile": "/logs/salad.log",
  "log_dir": "/logs",
  "version": "0.2.0",
  "debug": false,
  "features": {
    "ENABLE_HARDWARE_MONITORING": true,
    "ENABLE_GPU_DEMAND_API": true,
    "ENABLE_NETWORK_MONITORING": true,
    "ENABLE_PROCESS_MONITORING": true
  },
  "state": { /* ... */ }
}
```

## Prerequisites for Docker Desktop Windows

### 1. **NVIDIA GPU Support** (if using NVIDIA GPU)
```powershell
# Install NVIDIA Container Toolkit for Windows
# Download from: https://github.com/NVIDIA/nvidia-docker/releases

# Or via Chocolatey:
choco install nvidia-docker

# Verify installation:
docker run --rm --gpus all nvidia/cuda:11.8.0-runtime-windows-ltsc2022 nvidia-smi
```

### 2. **WSL 2 Backend** (Recommended)
- Docker Desktop for Windows uses WSL 2 by default (faster than Hyper-V)
- Ensure WSL 2 is installed and updated
- Graphics drivers must be installed on host Windows system

### 3. **Ports and Firewall**
- Port 8000 (API server) must be accessible
- Check Windows Firewall settings if accessing from other machines

## Directory Structure

```
salad-monitor/
├── Dockerfile              (original - Linux)
├── Dockerfile.windows      (Windows-optimized)
├── docker-compose.windows.yml
├── logs/                   (mount point for container logs)
├── config/                 (mount point for configs)
├── data/                   (mount point for persistent data)
├── .env.windows            (environment configuration)
└── [source files...]
```

## Quick Start

### 1. Create Environment Configuration
Copy the example environment file:
```bash
copy .env.windows.example .env.windows
```

Edit `.env.windows` with your settings:
```
LOG_DIR=/logs
DEBUG=false
ENABLE_HARDWARE_MONITORING=true
ENABLE_GPU_DEMAND_API=true
ENABLE_NETWORK_MONITORING=true
ENABLE_PROCESS_MONITORING=true
GPU_DEMAND_CACHE_MINUTES=5
```

### 2. Create Required Directories
```bash
mkdir logs
mkdir config
mkdir data
```

### 3. Build and Run

**Option A: Using docker-compose (Recommended)**
```bash
# Build the image
docker build -f Dockerfile.windows -t salad-monitor:latest .

# Start the container
docker-compose -f docker-compose.windows.yml up -d

# View logs
docker-compose -f docker-compose.windows.yml logs -f
```

**Option B: Using docker run directly**
```bash
docker run -d `
  --name salad-monitor `
  --gpus all `
  -p 8000:8000 `
  -v "$(pwd)/logs:/logs" `
  -v "$(pwd)/config:/config" `
  -v "$(pwd)/data:/app/data" `
  --env-file .env.windows `
  --restart unless-stopped `
  salad-monitor:latest
```

### 4. Verify Deployment
```bash
# Check container is running
docker ps | findstr salad-monitor

# View container logs
docker logs salad-monitor

# Test API endpoint
curl http://localhost:8000/api/v1/health
```

### 5. Stop the Container
```bash
# Using docker-compose
docker-compose -f docker-compose.windows.yml down

# Or using docker
docker stop salad-monitor
docker rm salad-monitor
```

## Hardware Monitoring on Docker Desktop Windows

### What Works
- ✅ **CPU Metrics**: Load percentage (psutil)
- ✅ **RAM Metrics**: Usage and percentage (psutil)
- ✅ **Disk Metrics**: Usage and percentage (psutil)
- ✅ **GPU Detection**: Basic GPU name (with NVIDIA Container Toolkit)
- ✅ **Process Monitoring**: Basic process detection

### What Has Limitations
- ⚠️ **GPU Metrics**: Require NVIDIA Container Toolkit + NVIDIA GPU
  - nvidia-smi only works if NVIDIA drivers are properly configured on host
  - GPU utilization, power, temperature may not be available in all configurations
  
- ⚠️ **CPU Name**: Limited (Windows Registry not accessible in container)
  - Fallback to generic "CPU" name
  
- ⚠️ **WSL Status**: Cannot detect WSL processes from inside container
  - Only works when monitoring from Windows host directly
  
- ⚠️ **Network Monitoring**: Limited to container's network interface
  - Host network metrics not directly accessible
  - Requires WSL 2 bridge configuration for accurate readings

### GPU Support Setup

#### For NVIDIA GPUs
```yaml
# In docker-compose.windows.yml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all  # or specific count
          capabilities: [gpu]

# Environment variables
environment:
  NVIDIA_VISIBLE_DEVICES: all
  NVIDIA_DRIVER_CAPABILITIES: compute,utility
```

**Troubleshooting:**
```bash
# Test GPU access inside container
docker exec salad-monitor nvidia-smi

# If it fails, check host GPU:
nvidia-smi

# Re-install NVIDIA Container Toolkit:
# On Windows: Settings → Resources → WSL Integration
```

## API Endpoints

All endpoints available at `http://localhost:8000/api/v1/`:

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | System health and feature flags |
| `GET /hardware` | CPU, RAM, GPU, Disk metrics |
| `GET /wallet` | Wallet balance and earnings |
| `GET /job` | Current job details |
| `GET /download` | Container download progress |
| `GET /network` | Network statistics |
| `GET /wsl` | WSL status (Windows only) |
| `GET /gpu-demand` | GPU demand data |
| `GET /processes` | Salad process info |
| `GET /logs` | List available logs |
| `GET /tail` | Last N lines of current log |

## Environment Variables

### Core Configuration
- `LOG_DIR` - Log directory path (default: `/logs`)
- `DEBUG` - Enable debug logging (default: `false`)

### Feature Flags
- `ENABLE_HARDWARE_MONITORING` (default: `true`)
- `ENABLE_GPU_DEMAND_API` (default: `true`)
- `ENABLE_NETWORK_MONITORING` (default: `true`)
- `ENABLE_PROCESS_MONITORING` (default: `true`)

### GPU Configuration
- `NVIDIA_VISIBLE_DEVICES` - Which GPUs to expose (default: `all`)
- `NVIDIA_DRIVER_CAPABILITIES` - GPU capabilities (default: `compute,utility`)
- `GPU_DEMAND_CACHE_MINUTES` - API cache duration (default: `5`)

## Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|-----------------|---------|
| `./logs` | `/logs` | Store application logs |
| `./config` | `/config` | Configuration files |
| `./data` | `/app/data` | Persistent data storage |

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs salad-monitor

# Check image
docker images | findstr salad-monitor

# Rebuild
docker build -f Dockerfile.windows -t salad-monitor:latest .
```

### API Returns Hardware Errors
```bash
# Check if hardware monitoring is enabled
curl http://localhost:8000/api/v1/health | grep ENABLE_HARDWARE_MONITORING

# If disabled, update environment and restart
docker restart salad-monitor
```

### GPU Not Detected
```bash
# Verify NVIDIA Container Toolkit
docker run --rm --gpus all nvidia/cuda:11.8.0-runtime-windows nvidia-smi

# If it works but our container doesn't:
# 1. Ensure --gpus all is set in docker-compose or run command
# 2. Check if nvidia-smi path is correct (Linux: /usr/bin/nvidia-smi)
# 3. Update NVIDIA drivers on host Windows system
```

### Log Files Not Persisting
```bash
# Verify volume mount
docker inspect salad-monitor | findstr "Mounts" -A 20

# Ensure host directory exists
ls -la logs

# Check container can write
docker exec salad-monitor ls -la /logs
```

## Performance Considerations

### Memory
- Base Python 3.11 image: ~150 MB
- With dependencies: ~400-500 MB
- Recommended allocation: 2-4 GB for comfortable operation

### CPU
- Monitor loop runs every 1-2 seconds
- Minimal CPU impact (<1% idle, <5% under load)
- Recommended: 2+ CPU cores

### Storage
- Logs grow based on activity frequency
- Plan for 100-500 MB per day of logs
- Clean up old logs regularly

## Production Deployment

### Docker Compose Override
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  salad-monitor:
    # ... base config from docker-compose.windows.yml ...
    
    # Production-specific settings
    environment:
      DEBUG: "false"
      LOG_DIR: /logs
    
    volumes:
      # Use named volumes for production
      - salad-logs:/logs
      - salad-data:/app/data
    
    # Stricter health checks
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 20s
      timeout: 5s
      retries: 5

volumes:
  salad-logs:
  salad-data:
```

### Run Production Stack
```bash
docker-compose -f docker-compose.windows.yml -f docker-compose.prod.yml up -d
```

## Common Docker Commands

### Container Management
```bash
# Start container
docker-compose -f docker-compose.windows.yml up -d

# Stop container
docker-compose -f docker-compose.windows.yml down

# Restart container
docker-compose -f docker-compose.windows.yml restart

# View container status
docker ps | findstr salad-monitor

# View container resource usage
docker stats salad-monitor --no-stream
```

### Monitoring and Logging

**View Real-time Logs**
```bash
docker logs -f salad-monitor
```

**View Last 50 Lines**
```bash
docker logs --tail 50 salad-monitor
```

**Save Logs to File**
```bash
docker logs salad-monitor > salad-monitor.log 2>&1
```

**Access Logs from Mounted Directory**
```bash
# Logs are in ./logs directory on host
type logs\salad.log
```

**Check Container Health**
```bash
docker inspect salad-monitor --format='{{.State.Health.Status}}'
```

### Rebuilding and Cleanup

**Rebuild Docker Image**
```bash
docker build -f Dockerfile.windows -t salad-monitor:latest .
```

**Remove Old Images**
```bash
docker rmi salad-monitor:latest
```

**Clean Up Volumes and Data**
```bash
# Remove container and volumes
docker-compose -f docker-compose.windows.yml down -v

# Or manually remove
docker volume rm <volume_name>
```

**Clear Log Files**
```bash
# WARNING: This deletes all logs from the host
del /S logs\*

# Or from PowerShell
Remove-Item logs\* -Force -Recurse
```

## Additional Resources

- [Docker Official Documentation](https://docs.docker.com/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [WSL 2 Integration Guide](https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
