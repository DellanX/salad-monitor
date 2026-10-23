# Compilation Issues in Salad Monitor

## Overview

The salad-monitor service has several compilation issues that prevent it from building successfully. These issues are primarily related to dependency version conflicts and API changes in external crates.

## Issues Identified

### 1. NVML Wrapper Compatibility Issues
```
error[E0432]: unresolved import `nvml_wrapper::enums::device::TemperatureSensor`
 --> crates/salad-collect/src/nvml_collector.rs:7:5
  |
7 | use nvml_wrapper::enums::device::TemperatureSensor;
  |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^-----------------
  |                                  |
  |                                  no `TemperatureSensor` in `enums::device`

error[E0603]: enum `UsedGpuMemory` is private
   --> crates/salad-collect/src/nvml_collector.rs:140:68
    |
140 | ..._wrappers::device::UsedGpuMemory::Used(b) => {
    |                       ^^^^^^^^^^^^^  ---- tuple variant `Used` is not publicly re-exported
```

### 2. Missing Dependencies
```
error[E0433]: cannot find module or crate `uuid` in this scope
  --> crates/salad-webhook/src/dispatcher.rs:53:22
   |
53 |         let log_id = uuid::Uuid::new_v4().to_string();
   |                      ^^^^ use of unresolved module or unlinked crate `uuid`

error[E0433]: cannot find module or crate `hex` in this scope
  --> crates/salad-webhook/src/dispatcher.rs:34:9
   |
34 |         hex::encode(result.into_bytes())
   |         ^^^ use of unresolved module or unlinked crate `hex`
```

### 3. Sysinfo Crate API Changes
```
error[E0599]: no method named `refresh_cpu_all` found for struct `sysinfo::System` in the current scope
  --> crates/salad-collect/src/sysinfo_collector.rs:71:13
   |
71 |         sys.refresh_cpu_all();
   |             ^^^^^^^^^^^^^^^
   |
help: there is a method `refresh_all` with a similar name

error[E0599]: no method named `global_cpu_usage` found for struct `sysinfo::System` in the current scope
  --> crates/salad-collect/src/sysinfo_collector.rs:93:34
   |
93 |         let cpu_usage = self.sys.global_cpu_usage();
   |                                  ^^^^^^^^^^^^^^^^
   |
help: there is a method `global_cpu_info` with a similar name
```

## Recommended Fixes

### 1. Update Dependencies in Cargo.toml

In `Cargo.toml`, update the following dependencies:

```toml
[dependencies]
# ... existing dependencies ...
uuid = { version = "1.0", features = ["v4"] }
hex = "0.4"
nvml-wrapper = "0.13.0"  # or compatible version
sysinfo = "0.30.0"       # or compatible version
```

### 2. Fix the NVML Wrapper Usage

In `crates/salad-collect/src/nvml_collector.rs`, update the imports and usage patterns to match the current API of nvml-wrapper.

### 3. Update Sysinfo Collector Methods

In `crates/salad-collect/src/sysinfo_collector.rs`:

- Replace `sys.refresh_cpu_all()` with `sys.refresh_all()`
- Replace `self.sys.global_cpu_usage()` with `self.sys.global_cpu_info()`

## Alternative Approach

Since the compilation issues are significant, you could:

1. Try using a different version of the crates that's compatible
2. Use Docker to run the service in a properly configured environment
3. Focus on the API endpoints and test them using mock data

## Running the Service (Once Fixed)

After fixing the compilation issues, you can run the service with:

```bash
# Build the release version
cargo build --bin salad-monitord --release

# Run the service
cargo run --bin salad-monitord --release
```

The service will start on port 8765 and provide RESTful endpoints for querying system telemetry.