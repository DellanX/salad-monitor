"""FastAPI application factory and startup configuration."""

import threading
from fastapi import FastAPI

from src.config import debug, resolve_log_dir
from src.api.routes import router
from src.monitor import monitor_logs


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Salad Monitor", description="GPU workload monitoring API")

    app.include_router(router)

    @app.on_event("startup")
    def start_monitor():
        log_dir = resolve_log_dir()
        debug(f"[startup] Launching monitor thread for directory: {log_dir}")
        threading.Thread(target=monitor_logs, daemon=True).start()

    return app


app = create_app()
