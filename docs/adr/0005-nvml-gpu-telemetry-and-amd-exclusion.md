# ADR 0005: NVML GPU Telemetry and AMD Exclusion

## Context
GPU telemetry is vital for Salad node monitoring. SaladXRay used `nvidia-smi` shelling out for NVIDIA GPUs and fell back to Windows `Win32_VideoController` and `PerformanceCounter("GPU Engine")` for AMD GPUs.

## Decision
1. Standardize on `nvml-wrapper` 0.13 for NVIDIA GPUs. It dynamically loads `nvml.dll` / `libnvidia-ml.so.1` at runtime, enabling GPU telemetry both natively on Windows and inside Linux Docker containers with NVIDIA Container Toolkit.
2. Exclude AMD GPUs from `salad-monitor` v1.0. AMD telemetry libraries in Rust (`libdrm`, sysfs) are Linux-only and incompatible with Windows native hosts, creating non-portable OS dependencies. Non-NVIDIA hosts report `gpu_nvidia: false`.

## Consequences
- High-fidelity NVIDIA telemetry (core load, VRAM, power, temp, PCIe throughput, per-PID compute/graphics processes).
- Zero build-time CUDA/NVML SDK requirements.
- Clean fallback on systems without NVIDIA GPUs.
- AMD GPUs are unsupported in v1.0.
