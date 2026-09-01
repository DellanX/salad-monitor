# ADR 0002: In-RAM Ring Buffer Metric History

## Context
Real-time web graphing requires historical metric points (e.g. GPU utilization over time). Storing time-series metric data in SQLite leads to disk I/O, wear on SSDs/flash storage, and higher RAM/CPU overhead.

## Decision
Keep historical metric points in bounded in-memory ring buffers (`std::collections::VecDeque` capped at 360 samples = 12 minutes). SQLite is reserved strictly for webhook configuration and state persistence.

## Consequences
- Idle RAM footprint stays under 32 MB.
- Zero disk write activity for telemetry streaming.
- Metric history is cleared when the daemon restarts.
