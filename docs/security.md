# Security Architecture & Specifications (`docs/security.md`)

This document outlines the security design for `salad-monitor` v1.0, covering authentication, secret persistence, password hashing, JWT token lifecycle, rate limiting, CORS, and network binding policies.

---

## 1. Secret Generation & Bootstrap Lifecycle

`salad-monitor` uses a **persistent master secret** model for authentication.

### Bootstrap Procedure:
1. At daemon startup, `salad-monitor` checks for an environment variable `SALAD_MONITOR_SECRET`.
2. If absent, it checks `config/secret.key` (or `%PROGRAMDATA%\SaladMonitor\secret.key` on Windows).
3. If no key file exists, `salad-monitor` generates a 256-bit cryptographically secure random secret (using Rust's `rand::rngs::OsRng`), encodes it as hex (64 characters), writes it to `secret.key` with restricted file permissions (`0600` on Unix, restricted ACL on Windows), and logs an informational notice with the key fingerprint (SHA-256 hash prefix).
4. The secret is **never logged in plain text** or returned via API endpoints.

---

## 2. Password & Secret Hashing (`argon2`)

For UI password/PIN login (`POST /api/v1/auth/login`), the daemon verifies the submitted secret against the master secret.

- **Algorithm**: Argon2id (`argon2` crate)
- **Parameters**:
  - Memory size: 19 MiB (`19456` KB) — optimized for low RAM daemon footprint
  - Iteration count (t_cost): 2 passes
  - Parallelism (p_cost): 1 thread
  - Output length: 32 bytes

---

## 3. JSON Web Token (JWT) Specifications

Upon successful login, `POST /api/v1/auth/login` returns a signed JWT access token.

- **Algorithm**: HMAC-SHA256 (`HS256` via `jsonwebtoken` crate)
- **Signing Key**: Derived from the master secret (SHA-256 hash of secret + `"jwt_signing_key_salt"`)
- **Token Claims**:
  ```json
  {
    "sub": "salad-monitor-user",
    "iss": "salad-monitor-daemon",
    "iat": 1788280000,
    "exp": 1788283600,
    "jti": "random_uuid_v4"
  }
  ```
- **Time To Live (TTL)**: 1 hour (`3600` seconds).
- **Refresh Flow**: `POST /api/v1/auth/refresh` issues a new token if the current token is valid or expired within a 5-minute grace window.

---

## 4. Rate Limiting (`tower_governor`)

`salad-monitor` uses `tower_governor` middleware to defend HTTP and SSE routes against brute-force attacks and denial-of-service attempts.

| Route / Tier | Max Burst | Replenish Rate | Action on Exceed |
|---|---|---|---|
| `POST /api/v1/auth/login` | 5 requests | 1 request per 10 seconds | 429 Too Many Requests |
| `GET /api/v1/stream` (SSE) | 10 connections | 1 conn per 2 seconds | 429 Too Many Requests |
| General REST API (`/api/v1/*`) | 60 requests | 2 requests per second | 429 Too Many Requests |
| Static UI Assets (`/`, `/assets/*`)| 100 requests | 10 requests per second | 429 Too Many Requests |

---

## 5. Network Binding & CORS Policies

- **Default Bind Address**: `127.0.0.1:8000` (Loopback only).
- **Docker Bind Address**: `0.0.0.0:8000` (Configurable via `BIND_ADDRESS` env var).
- **CORS Configuration**:
  - By default, CORS allows requests only from the same origin.
  - If `ALLOWED_ORIGINS` environment variable is set (e.g. `http://localhost:3000`), `tower-http::cors::CorsLayer` enables configured origins with allowed headers `Authorization`, `Content-Type`, `X-Salad-Signature`.

---

## 6. Threat Model & Risk Mitigations

| Threat | Vulnerability | Mitigation |
|---|---|---|
| Brute-forcing login PIN | Weak user password | Argon2id hashing + 5 req/min rate limit on `/auth/login` |
| Master key compromise | Key checked into git | Key auto-generated outside git root with `0600` permissions; `.gitignore` includes `config/*.key` |
| Insecure Webhook HTTP endpoints | Eavesdropping / forgery | HMAC-SHA256 payload signing (`X-Salad-Signature`); HTTPS enforced for non-localhost webhooks |
| High RAM consumption attack | Large SSE subscriber count | Bounded `tokio::sync::broadcast` buffer (max 100 queued messages per subscriber; lagging subscribers dropped) |
