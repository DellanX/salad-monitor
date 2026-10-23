# `ui` Vue 3 SPA Specification

`ui` is a Vue 3 + Vite + TypeScript single-page application embedded into `salad-monitord` via `rust-embed`.

## Features:
- Subscribes to `/api/v1/stream` SSE stream with automatic reconnection.
- Pinia store managing telemetry snapshot and in-RAM graph history.
- Real-time dashboard mirroring SaladXRay's panel layout (Earnings, Container Workload, Global Hardware, GPU Demand, WSL, Network, Processes, Events).
- Capability-aware rendering: greys out panels when underlying capability is `false` (e.g. WSL in Docker).
- Webhook management interface.
