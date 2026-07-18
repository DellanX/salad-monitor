# 🥗 Salad Monitor

A lightweight FastAPI service that monitors your Salad GPU workload and exposes a clean `/health` API endpoint for Home Assistant or other automation systems.

This service watches your Salad logs, tracks GPU activity, workload state, and version information, and provides a simple JSON API for external systems.

---

## 🚀 Features

- Real‑time monitoring of Salad GPU activity
- Parses Salad log files for:
  - Active workload state
  - Pending workload state
  - GPU reservation state
  - Last event
  - Current logfile
- Clean REST API:
  - `GET /health`
  - `GET /version`
- Lightweight FastAPI server
- Docker‑ready
- Works seamlessly with the **Salad Monitor Home Assistant Integration**
- Zero external dependencies beyond Python + FastAPI

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

### Environment Variables (optional)

| Variable  | Description                         | Default |
| --------- | ----------------------------------- | ------- |
| `LOG_DIR` | Path to Salad logs inside container | `/logs` |
| `PORT`    | API port                            | `8000`  |
| `DEBUG`   | Enable debug mode                   | `false` |

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
```

## Home Assistant Integration

https://github.com/dellanx/salad-monitor-ha
