# System Architecture (`docs/architecture.md`)

This document outlines the high-level design, crate architecture, data flow, and concurrency model for `salad-monitor` v1.0.

---

## 1. High-Level Architecture Overview

`salad-monitor` v1.0 collapses the legacy Python FastAPI daemon + Windows sidecar process into a **single Rust executable** (`salad-monitord`) with an embedded Vue 3 SPA web UI (`salad-monitor-ui`).

```
 +-------------------------------------------------------------------+
 |                       salad-monitord (Rust)                       |
 |                                                                   |
 |  +--------------------+   +-------------------+  +-------------+  |
 |  |  salad-collect     |   |  salad-logparse   |  | salad-webhk |  |
 |  |  (sysinfo, NVML,   |   |  (Salad log text  |  | (rusqlite,  |  |
 |  |   WMI, demand API) |   |   regex state)    |  |  dispatcher)|  |
 |  +---------+----------+   +---------+---------+  +------+------+  |
 |            |                        |                   |         |
 |            +-------------------+----+-------------------+         |
 |                                |                                  |
 |                                v                                  |
 |                     Shared Snapshot State                         |
 |                    Arc<RwLock<Snapshot>>                          |
 |                                |                                  |
 |          +---------------------+---------------------+            |
 |          |                                           |            |
 |          v                                           v            |
 |   Axum REST & SSE                            mdns-sd (mDNS)       |
 |   (/api/v1/stream)                        (_salad-monitor._tcp)   |
 |          |                                                        |
 |          v                                                        |
 |   rust-embed Vue 3 SPA (HTML/JS/CSS)                              |
 +-------------------------------------------------------------------+
```

---

## 2. Workspace Crate Division

The repository is structured as a Cargo workspace containing four Rust crates and one Vue SPA project:

1. **`crates/salad-monitord` (Binary Crate)**:
   - Axum HTTP web server & SSE streaming handlers.
   - Authentication middleware (JWT & Argon2id).
   - Async tick scheduler (`1s`, `2s`, `10s` collection loops).
   - Asset embedding via `rust-embed`.

2. **`crates/salad-collect` (Library Crate)**:
   - Platform-abstracted collectors.
   - Cross-platform system metrics via `sysinfo`.
   - GPU telemetry via `nvml-wrapper` 0.13.
   - Windows-specific WMI & registry lookups (`cfg(windows)`).
   - Salad HTTP demand API client (`https://app-api.salad.com`).

3. **`crates/salad-logparse` (Library Crate)**:
   - Pure, zero-side-effect log parsing state machine.
   - Incremental log file tailing with rotation detection.
   - Regex extractors for Salad Bowl log patterns.
   - Workload state, pull progress, and download ETA calculations.

4. **`crates/salad-webhook` (Library Crate)**:
   - SQLite database management via `rusqlite` (bundled).
   - Webhook registration CRUD logic and migrations.
   - Event bus subscriber & HMAC-SHA256 retry dispatcher.

5. **`ui/` (Vue 3 SPA)**:
   - Vue 3 + Vite + TypeScript + Pinia frontend.
   - Real-time dashboard mirroring SaladXRay panel layout.
   - SSE connection management with auto-reconnect.
   - Capability-gated UI components.

---

## 3. Data Flow & Concurrency Model

1. **Shared State**: The global telemetry snapshot is stored in an `Arc<RwLock<Snapshot>>`.
2. **Tick Scheduler**: A background Tokio task runs three concurrent collection loops:
   - **Fast Tick (1s)**: Incremental log tailing, uptime calculations, download progress ETA.
   - **Medium Tick (2s)**: NVML GPU telemetry, process miner checks, network I/O stats.
   - **Slow Tick (10s)**: `sysinfo` CPU/RAM/disk metrics, WSL status, process version queries.
   - **Demand Tick (5m)**: Salad GPU demand API query (`app-api.salad.com`).
3. **SSE Fan-Out**: When a collection tick completes, updated fields are sent to `tokio::sync::broadcast` channel. Axum SSE subscriber handlers receive delta events and push them to web browsers.
4. **Webhook Dispatching**: State change events (e.g. `job_started`, `error_detected`) are published to the webhook queue, where a background worker signs payloads with HMAC-SHA256 and POSTs them to configured URLs with exponential backoff.

---

## 4. Architectural Decision Records (ADRs)

See `docs/adr/` for detailed rationale:
- `0001-no-sidecar-single-binary.md`: Eliminating the sidecar in favor of platform-abstracted collectors in a single binary.
- `0002-in-ram-ring-buffer-history.md`: Using in-memory ring buffers for graph history to keep RAM low and prevent SQLite wear.
- `0003-rusqlite-over-sqlx.md`: Choosing synchronous bundled `rusqlite` over heavy compile-time `sqlx`.
- `0004-pure-rust-mdns-sd.md`: Adopting `mdns-sd` for zero-dependency mDNS autodiscovery.
- `0005-nvml-gpu-telemetry-and-amd-exclusion.md`: Standardizing on `nvml-wrapper` 0.13 for NVIDIA and excluding AMD.
