"""FastAPI application factory and startup configuration."""

import threading
from fastapi import FastAPI

from src.config import debug, resolve_log_dir, COLLECTOR_MODE
from src.api.routes import router as legacy_router
from src.api.routes_v1 import router as v1_router
from src.monitor import monitor_logs
from src import state as state_module


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Salad Monitor",
        description="GPU workload monitoring API with enhanced metrics",
        version="0.2.0"
    )

    # Include legacy routes (no prefix for backward compatibility)
    app.include_router(legacy_router)
    
    # Include new v1 routes with /api/v1 prefix
    app.include_router(v1_router)

    @app.on_event("startup")
    def start_monitor():
        log_dir = resolve_log_dir()
        state_module.set_collector_mode(COLLECTOR_MODE)
        debug(f"[startup] Launching monitor thread for directory: {log_dir}")
        threading.Thread(target=monitor_logs, daemon=True).start()

    return app


app = create_app()
