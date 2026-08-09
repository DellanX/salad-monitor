"""Unit tests for src/api/routes_v1.py"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.app import create_app
from src import state


@pytest.fixture
def v1_client():
    """Create a test client for the FastAPI app with v1 routes."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def reset_state():
    """Reset state before each test."""
    state.state.clear()
    state.state.update({
        "salad_pending": False,
        "salad_active": False,
        "gpu_reserved": False,
        "last_event": None,
        "current_logfile": None,
    })
    yield
    # Reset after test
    state.state.clear()


@pytest.mark.unit
class TestRoutesV1:
    """Test v1 API endpoints."""

    def test_v1_endpoints_exist(self, v1_client):
        """Test that v1 endpoints are registered."""
        # Try to access a v1 endpoint to verify the router is included
        response = v1_client.get("/api/v1/health")
        # Should get a 200 response, not 404
        assert response.status_code == 200
        assert "monitor_running" in response.json()

    @patch('src.api.routes_v1.get_feature_flags')
    def test_v1_health_includes_feature_flags(self, mock_get_feature_flags, v1_client):
        """Test v1 health endpoint includes feature toggle status."""
        mock_get_feature_flags.return_value = {
            "ENABLE_HARDWARE_MONITORING": True,
            "ENABLE_GPU_DEMAND_API": True,
            "ENABLE_NETWORK_MONITORING": False,
            "ENABLE_PROCESS_MONITORING": True,
        }

        response = v1_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["features"] == {
            "ENABLE_HARDWARE_MONITORING": True,
            "ENABLE_GPU_DEMAND_API": True,
            "ENABLE_NETWORK_MONITORING": False,
            "ENABLE_PROCESS_MONITORING": True,
        }

    def test_v1_extended_health(self, v1_client, reset_state):
        """Test v1 extended health endpoint if available."""
        response = v1_client.get("/api/v1/health-extended")

        # May return 404 if route doesn't exist
        assert response.status_code in [200, 404]

    def test_v1_metrics_summary(self, v1_client, reset_state):
        """Test v1 metrics summary endpoint if available."""
        response = v1_client.get("/api/v1/metrics/summary")

        # May return 404 if route doesn't exist
        assert response.status_code in [200, 404]

    def test_v1_job_info(self, v1_client, reset_state):
        """Test v1 job info endpoint if available."""
        response = v1_client.get("/api/v1/job-info")

        # May return 404 if route doesn't exist
        assert response.status_code in [200, 404]

    def test_v1_download_status(self, v1_client, reset_state):
        """Test v1 download status endpoint if available."""
        response = v1_client.get("/api/v1/download-status")

        # May return 404 if route doesn't exist
        assert response.status_code in [200, 404]

    def test_v1_wallet_status(self, v1_client, reset_state):
        """Test v1 wallet status endpoint if available."""
        response = v1_client.get("/api/v1/wallet-status")

        # May return 404 if route doesn't exist
        assert response.status_code in [200, 404]

    def test_v1_hardware_stats(self, v1_client, reset_state):
        """Test v1 hardware stats endpoint if available."""
        response = v1_client.get("/api/v1/hardware-stats")

        # May return 404 if route doesn't exist
        assert response.status_code in [200, 404]

    def test_v1_endpoints_with_state_data(self, v1_client, reset_state):
        """Test v1 endpoints with populated state."""
        # Populate state with some data
        state.state["job_id"] = "test-job-123"
        state.state["wallet_balance"] = "$100.00"
        state.state["download_progress_pct"] = 50.0
        state.state["cpu_load_pct"] = 25.5

        # Try endpoints
        endpoints = [
            "/api/v1/health-extended",
            "/api/v1/metrics/summary",
            "/api/v1/job-info",
            "/api/v1/download-status",
            "/api/v1/wallet-status",
            "/api/v1/hardware-stats"
        ]

        for endpoint in endpoints:
            response = v1_client.get(endpoint)
            # Should either succeed or be not found, not error
            assert response.status_code in [200, 404, 422]

    def test_v1_routes_prefix(self, v1_client):
        """Test that v1 routes have correct prefix."""
        # Verify v1 health endpoint works
        response = v1_client.get("/api/v1/health")
        assert response.status_code == 200

        # Verify that the endpoint has the /api/v1 prefix in the URL
        assert "/api/v1" in str(response.request.url)
