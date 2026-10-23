# ADR 0001: Eliminate Sidecar in Favor of Single Binary with Capability Model

## Context
Salad Monitor v0.x used a 2-process architecture: a Python FastAPI server running inside a Linux Docker container and a separate Python "sidecar" running natively on Windows host to collect metrics via WMI/perf counters and push them over HTTP. This required maintaining two processes, synchronized versioning, and complex installation scripts.

## Decision
Collapse to a single Rust daemon binary (`salad-monitord`) that runs either natively on Windows or inside a Docker container. Host capabilities are detected dynamically at startup.

## Consequences
- Single binary deployment for both Windows native `.exe` and Docker container.
- Zero sidecar maintenance.
- In Docker containers, host-specific metrics (WMI, registry) degrade gracefully to `null` and report `false` in `/api/v1/capabilities`.
