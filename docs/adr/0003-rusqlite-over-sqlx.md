# ADR 0003: Use Bundled `rusqlite` Over `sqlx`

## Context
The application needs SQLite persistence for storing webhook registrations and webhook delivery logs. Async ORMs like `sqlx` add significant macro compile times, async driver complexity, and binary bloat.

## Decision
Use `rusqlite` with the `bundled` feature flag. Database operations are synchronous and executed off the main async event loop using `tokio::task::spawn_blocking`.

## Consequences
- Fast compile times and small executable size.
- Self-contained SQLite build with no system C-library dependencies.
- Simple, explicit SQL schema and migrations.
