# Multi-stage Dockerfile for salad-monitord daemon + embedded Vue 3 SPA

# Stage 1: Build Vue 3 static SPA assets
FROM node:20-alpine AS ui-builder
WORKDIR /app/ui
COPY ui/package*.json ./
RUN npm ci
COPY ui/ ./
RUN npm run build

# Stage 2: Rust builder
FROM rust:1.80-slim AS rust-builder
WORKDIR /usr/src/salad-monitor

# Install build tools & dependencies
RUN apt-get update && apt-get install -y pkg-config libssl-dev build-essential && rm -rf /var/lib/apt/lists/*

COPY Cargo.toml Cargo.lock ./
COPY crates ./crates
COPY --from=ui-builder /app/ui/dist ./ui/dist

# Build release binary
RUN cargo build --release -p salad-monitord

# Stage 3: Minimal runtime container
FROM debian:bookworm-slim
WORKDIR /app

RUN apt-get update && apt-get install -y ca-certificates sqlite3 libssl3 && rm -rf /var/lib/apt/lists/*

# Crucial: NVIDIA Container Toolkit requires NVIDIA_DRIVER_CAPABILITIES=utility,compute to mount libnvidia-ml.so.1
ENV NVIDIA_DRIVER_CAPABILITIES=utility,compute
ENV NVIDIA_VISIBLE_DEVICES=all
ENV RUST_LOG=info

COPY --from=rust-builder /usr/src/salad-monitor/target/release/salad-monitord /app/salad-monitord

EXPOSE 8765

ENTRYPOINT ["/app/salad-monitord"]
