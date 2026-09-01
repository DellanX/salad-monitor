# `salad-webhook` Library Crate Specification

`salad-webhook` handles persistent webhook storage and secure async notification dispatch.

## Modules:
- `db`: Synchronous SQLite database access (`rusqlite`) for CRUD operations on registered webhooks.
- `dispatcher`: Tokio async task subscribing to event bus, computing HMAC-SHA256 signatures (`X-Salad-Signature`), and delivering POST requests with exponential backoff.
