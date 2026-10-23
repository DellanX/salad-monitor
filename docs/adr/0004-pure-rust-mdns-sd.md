# ADR 0004: Pure Rust `mdns-sd` for Autodiscovery

## Context
Multi-node discovery requires advertising local monitor services over mDNS (`_salad-monitor._tcp.local.`). System mDNS daemons (Avahi on Linux, Bonjour / mDNSResponder on Windows) are frequently absent in minimal environments like WSL2 or Docker containers.

## Decision
Use `mdns-sd`, a pure Rust implementation of multicast DNS service discovery.

## Consequences
- Zero external daemon dependencies.
- Works identically across Windows native, WSL2, Linux, and Docker containers.
- Supports multi-instance collision resolution and metadata TXT records.
