# Validation & Manual Testing Guide: Salad Monitor v1.0

This document contains step-by-step verification instructions to be executed on a Rust- and Docker-capable test machine.

---

## 1. Automated Rust & Workspace Tests

Run the full workspace unit and integration test suite:

```bash
# Check code formatting across all crates
cargo fmt --all --check

# Run Clippy lints across all crates
cargo clippy --workspace --all-targets -- -D warnings

# Execute all crate unit tests and integration tests
cargo test --workspace -- --nocapture
```

Expected output:
- `salad-logparse`: 5 passed
- `salad-collect`: 3 passed
- `salad-webhook`: 2 passed
- `salad-monitord`: 1 passed

---

## 2. Vue 3 SPA Build Verification

```bash
cd ui
npm ci
npm run build
```

Expected output: `dist/` directory generated containing `index.html` and bundled `assets/`.

---

## 3. NVML GPU Telemetry Validation Checklist

Run `salad-monitord` on a machine with an NVIDIA GPU:

```bash
cargo run --release -p salad-monitord
```

Perform the following empirical checks:

- [ ] **Device Detection**: Query `http://localhost:8765/api/v1/snapshot`. Confirm `gpu.is_available` is `true` and `gpu.devices[0].uuid` starts with `GPU-`.
- [ ] **Power & Temperature**: Verify `power_usage_w` > 0.0 and `temperature_c` is realistic (25-85°C).
- [ ] **VRAM Memory Usage**: Confirm `memory_used_bytes` matches Task Manager / `nvidia-smi`.
- [ ] **Process Attribution**: Confirm `running_processes` lists active compute/graphics PIDs.

### Graceful Non-GPU Degradation Check
On a machine with no NVIDIA GPU (or with GPU disabled):
- [ ] Confirm `salad-monitord` starts cleanly without panicking.
- [ ] Query `/api/v1/capabilities`. Confirm `gpu_nvidia` is `false`.
- [ ] Query `/api/v1/snapshot`. Confirm `gpu.is_available` is `false` and `gpu.devices` is empty.

---

## 4. Salad Log Parsing & Container State Verification

1. Place sample Salad log in `C:\ProgramData\Salad\logs\log-2026-03-30.txt`.
2. Start `salad-monitord`.
3. Verify `/api/v1/snapshot` reflects:
   - `log_state.workload_id`
   - `log_state.global_progress`
   - `log_state.wallet_balance`
   - `log_state.status` ('running' / 'downloading')
