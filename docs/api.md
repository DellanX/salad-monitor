# REST, SSE, and Webhook API Specification (`docs/api.md`)

This document is the canonical contract for `salad-monitor` v1.0 HTTP endpoints, Server-Sent Events (SSE), and Webhook delivery mechanisms.

---

## 1. Overview & General Conventions

- **Base Path**: `/api/v1`
- **Content-Type**: `application/json` (except SSE streams: `text/event-stream` and static assets: `text/html`, `application/javascript`, etc.)
- **Error Response Envelope**: All non-2xx responses return a structured JSON error envelope:
  ```json
  {
    "error": {
      "code": "UNAUTHORIZED",
      "message": "Invalid or missing Bearer token",
      "details": null
    }
  }
  ```

---

## 2. Authentication & Authorization

Protected endpoints require a HTTP Bearer token header:
`Authorization: Bearer <jwt_or_persistent_secret>`

1. **Persistent Secret**: Defined in configuration (`SALAD_MONITOR_SECRET` or auto-generated at `config/secret.key`). Machine clients can pass this secret directly in the `Authorization` header.
2. **User Password / PIN Login**: Users log in via `/api/v1/auth/login` using the secret/password to receive a short-lived JWT (1 hour expiration).

Unauthenticated Endpoints:
- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- Static UI assets (`/`, `/assets/*`)

---

## 3. Endpoint Reference

### 3.1 Unauthenticated & Health Routes

#### `GET /api/v1/health`
Returns service health and collection status.
- **Auth**: None
- **Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 3600,
    "log_parsing_active": true,
    "gpu_monitoring_active": true
  }
  ```

#### `GET /api/v1/capabilities`
Returns host capabilities detected at daemon startup.
- **Auth**: None or Optional
- **Response (200 OK)**:
  ```json
  {
    "capabilities": {
      "log_parsing": true,
      "salad_demand_api": true,
      "gpu_nvidia": true,
      "gpu_per_process": true,
      "host_processes": true,
      "wsl_status": true,
      "windows_registry": true,
      "host_nic_vethernet": true,
      "disk_smart": true,
      "miner_detection": true
    }
  }
  ```

---

### 3.2 Authentication Routes

#### `POST /api/v1/auth/login`
Exchanges the system secret or configured user PIN for a short-lived JWT access token.
- **Auth**: None
- **Request Body**:
  ```json
  {
    "secret": "your_persistent_secret_here"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "token_type": "Bearer",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in_seconds": 3600
  }
  ```
- **Response (401 Unauthorized)**: Invalid secret.

#### `POST /api/v1/auth/refresh`
Refreshes a valid or recently expired JWT.
- **Auth**: Bearer JWT
- **Response (200 OK)**:
  ```json
  {
    "token_type": "Bearer",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in_seconds": 3600
  }
  ```

---

### 3.3 Telemetry & Data Routes

#### `GET /api/v1/snapshot`
Returns the full canonical telemetry snapshot.
- **Auth**: Bearer Token
- **Response (200 OK)**: Full `Snapshot` object (see `docs/metrics.md`).

#### `GET /api/v1/logs`
Lists available Salad log files.
- **Auth**: Bearer Token
- **Response (200 OK)**:
  ```json
  {
    "log_directory": "C:\\ProgramData\\Salad\\logs",
    "current_logfile": "log-2026-08-30.txt",
    "files": [
      {
        "filename": "log-2026-08-30.txt",
        "size_bytes": 1048576,
        "last_modified": "2026-08-30T14:05:00Z"
      }
    ]
  }
  ```

#### `GET /api/v1/logs/tail?lines=100`
Tails raw log lines from the current active log file.
- **Auth**: Bearer Token
- **Query Parameters**: `lines` (optional, default `50`, max `500`)
- **Response (200 OK)**:
  ```json
  {
    "filename": "log-2026-08-30.txt",
    "lines_returned": 2,
    "lines": [
      "2026-08-30 14:03:00.000 +00:00 [WRN] High GPU memory utilization detected",
      "2026-08-30 14:03:15.000 +00:00 [ERR] Network connection reset by peer"
    ]
  }
  ```

---

### 3.4 Server-Sent Events (SSE) Stream

#### `GET /api/v1/stream`
Establishes a continuous SSE connection for live telemetry updates.
- **Auth**: Bearer Token (passed via `Authorization: Bearer <token>` or query param `?token=<jwt>`)
- **Header**: `Accept: text/event-stream`

#### Event Types

1. **`snapshot`** (Emitted immediately upon connection):
   Contains the full initial snapshot and 12-minute in-RAM graph history.
   ```
   event: snapshot
   data: {"snapshot": {...}, "history": {"gpu_utilization": [...], "cpu_load": [...]}}
   ```

2. **`delta`** (Emitted on metric ticks, ~1s–2s):
   Contains only fields that changed since the previous tick.
   ```
   event: delta
   data: {"hardware": {"gpu_temperature_c": 68}, "job": {"uptime_seconds": 1240}}
   ```

3. **`log`** (Emitted instantly when a new log line is read):
   ```
   event: log
   data: {"timestamp": "2026-08-30T14:03:15Z", "line": "2026-08-30 14:03:15.000 +00:00 [ERR] Network connection reset"}
   ```

4. **`event`** (Emitted on major state transitions, e.g. job started/stopped, miner detected):
   ```
   event: event
   data: {"type": "job_started", "job_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab", "timestamp": "2026-08-30T14:02:14Z"}
   ```

5. **`heartbeat`** (Emitted every 15 seconds to keep connection alive):
   ```
   event: heartbeat
   data: {"timestamp": "2026-09-01T11:00:15Z"}
   ```

---

### 3.5 Webhook Management Routes

Webhooks allow external services (Home Assistant, Discord, custom daemons) to receive HTTP POST alerts on state transitions.

#### `GET /api/v1/webhooks`
Lists all registered webhooks.
- **Auth**: Bearer Token
- **Response (200 OK)**:
  ```json
  {
    "webhooks": [
      {
        "id": "wh_123456",
        "url": "https://example.com/webhook",
        "events": ["job_started", "job_stopped", "error_detected"],
        "enabled": true,
        "created_at": "2026-09-01T10:00:00Z"
      }
    ]
  }
  ```

#### `POST /api/v1/webhooks`
Registers a new webhook endpoint.
- **Auth**: Bearer Token
- **Request Body**:
  ```json
  {
    "url": "https://example.com/webhook",
    "secret": "custom_hmac_signing_secret_optional",
    "events": ["job_started", "job_stopped", "error_detected", "miner_detected"],
    "enabled": true
  }
  ```
- **Response (201 Created)**: Created webhook object.

#### `DELETE /api/v1/webhooks/{id}`
Deletes a registered webhook.
- **Auth**: Bearer Token
- **Response (204 No Content)**

#### `POST /api/v1/webhooks/{id}/test`
Triggers a test payload delivery to the specified webhook.
- **Auth**: Bearer Token
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "status_code": 200,
    "delivery_time_ms": 145
  }
  ```

---

## 4. Webhook Payload Signature & Contract

When an event fires, `salad-monitor` dispatches an HTTP POST request to registered webhook URLs.

### Headers:
- `Content-Type: application/json`
- `X-Salad-Event: <event_type>`
- `X-Salad-Signature: t=<timestamp>,v1=<hmac_sha256_hex>`

### HMAC Signature Computation:
The signature header contains the UNIX timestamp `t` and the HMAC-SHA256 hash `v1` of string `t.payload_json` signed with the webhook's `secret`.

### Example Webhook Body:
```json
{
  "event": "job_started",
  "timestamp": "2026-08-30T14:02:14Z",
  "job": {
    "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
    "container_status": "Running (Stable)"
  },
  "wallet": {
    "balance": 12.3456,
    "projected_24h": 0.4500
  }
}
```
