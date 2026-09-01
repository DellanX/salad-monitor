# `salad-monitord` Binary Crate Specification

`salad-monitord` is the main binary executable for Salad Monitor v1.0.

## Responsibilities:
- Spawns and supervises async telemetry collection loops (`1s`, `2s`, `10s`, `5m`).
- Serves Axum HTTP endpoints (`/api/v1/*`), SSE event stream (`/api/v1/stream`), and static web UI assets (`rust-embed`).
- Handles user authentication (Argon2id password hashing + JWT issue/verify).
- Manages rate-limiting middleware (`tower_governor`).
- Controls mDNS autodiscovery registration (`mdns-sd`).
