"""Shared test fixtures and configuration for pytest."""

import pytest
from fastapi.testclient import TestClient
from src.app import create_app
from src import state


@pytest.fixture
def app():
    """Create a FastAPI app instance for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_state():
    """Reset global state before and after each test."""
    # Reset before test
    state.state["salad_pending"] = False
    state.state["salad_active"] = False
    state.state["gpu_reserved"] = False
    state.state["last_event"] = None
    state.state["current_logfile"] = None
    
    yield
    
    # Reset after test
    state.state["salad_pending"] = False
    state.state["salad_active"] = False
    state.state["gpu_reserved"] = False
    state.state["last_event"] = None
    state.state["current_logfile"] = None


@pytest.fixture
def sample_log_lines():
    """Provide sample log lines for testing."""
    return [
        "[2024-01-01 12:00:00] INFO: System starting",
        "[2024-01-01 12:00:01] INFO: Workload received from server",
        "[2024-01-01 12:00:02] INFO: GPU HardwareCompatibility check passed",
        "[2024-01-01 12:00:03] INFO: Starting workload container",
        "[2024-01-01 12:05:00] INFO: Workload completed successfully",
    ]
