# mDNS Service Autodiscovery Specification (`docs/discovery.md`)

This document details the Multicast DNS (mDNS) autodiscovery mechanism in `salad-monitor` v1.0.

---

## 1. Overview & Goals

In multi-node Salad setups, multiple instances of `salad-monitor` may run simultaneously across different machines on a local network.

To allow web UIs, Home Assistant, and management tooling to automatically discover running monitor instances without hardcoding IP addresses:
- `salad-monitor` embeds a pure Rust mDNS implementation (`mdns-sd` crate).
- **No external system daemons** (such as Avahi, Bonjour, or Windows mDNS service) are required. This ensures instant setup on Windows, Linux, WSL2, and Docker containers.

---

## 2. mDNS Service Profile

| Field | Value / Format |
|---|---|
| Service Type | `_salad-monitor._tcp.local.` |
| Port | Default `8000` (or configured HTTP port) |
| Instance Name | `Salad Monitor ({hostname})` (e.g. `Salad Monitor (RIG-01)`) |
| Domain | `local.` |

---

## 3. TXT Records

The mDNS advertisement includes key-value TXT metadata:

```ini
version=1.0.0
instance_id=node_a1b2c3d4
hostname=RIG-01
capabilities=log_parsing,gpu_nvidia,wsl_status
tls_enabled=false
api_path=/api/v1
```

| TXT Key | Type | Description |
|---|---|---|
| `version` | string | Daemon release version |
| `instance_id` | string | Unique random node identifier (persisted in `config/instance.id`) |
| `hostname` | string | Local machine hostname |
| `capabilities` | string | Comma-separated active capabilities |
| `tls_enabled` | bool | `true` if HTTPS is configured |
| `api_path` | string | Base API path (`/api/v1`) |

---

## 4. Multi-Instance & Collision Resolution

When multiple nodes run `salad-monitor` on the same subnet:
1. `mdns-sd` performs a probe phase prior to registering the service name.
2. If `Salad Monitor (RIG-01)` is already registered on the network by another daemon, `mdns-sd` automatically appends a numeric suffix: `Salad Monitor (RIG-01) (2)`.
3. Node uniqueness is tracked via `instance_id` in TXT records rather than the human-readable instance name.

---

## 5. Container & WSL2 Networking Caveats

mDNS relies on UDP multicast traffic on port `5353`.

### Docker Desktop & Bridge Networks:
- Docker default bridge networking (`--net=bridge`) isolates multicast packets within the container network.
- **Recommendation**: To expose mDNS autodiscovery on Linux Docker hosts, run with `--net=host`.
- **Docker Desktop (Windows/macOS)**: Docker Desktop VM isolates mDNS. `salad-monitor` advertises inside the container network gracefully without failing.
- **Advertise Address Override**: Environment variable `MDNS_ADVERTISE_IP=192.168.1.100` can be set to force advertising the physical host IP address.

### Disabling mDNS (Opt-Out):
Set `ENABLE_MDNS=false` environment variable to completely disable mDNS advertisement.
