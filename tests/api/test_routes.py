"""Unit tests for src/api/routes.py"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.app import create_app
from src import state


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def reset_state():
    """Reset state before each test."""
    state.state["salad_pending"] = False
    state.state["salad_active"] = False
    state.state["gpu_reserved"] = False
    state.state["last_event"] = None
    state.state["current_logfile"] = None
    yield
    # Reset after test as well
    state.state["salad_pending"] = False
    state.state["salad_active"] = False
    state.state["gpu_reserved"] = False
    state.state["last_event"] = None
    state.state["current_logfile"] = None


@pytest.mark.unit
class TestAPIRoutes:
    """Test API route handlers."""

    def test_gpu_status(self, client, reset_state):
        """Test /gpu-status endpoint returns current state."""
        # Set some state
        state.state["salad_active"] = True
        state.state["last_event"] = "active"

        response = client.get("/gpu-status")

        assert response.status_code == 200
        data = response.json()
        assert data["salad_active"] is True
        assert data["last_event"] == "active"

    def test_current_logfile(self, client, reset_state):
        """Test /current-logfile endpoint."""
        test_path = "/logs/test.log"
        state.state["current_logfile"] = test_path

        response = client.get("/current-logfile")

        assert response.status_code == 200
        data = response.json()
        assert data["current_logfile"] == test_path

    def test_current_logfile_none(self, client, reset_state):
        """Test /current-logfile when no logfile is set."""
        response = client.get("/current-logfile")

        assert response.status_code == 200
        data = response.json()
        assert data["current_logfile"] is None

    @patch('src.api.routes.read_logfile_lines')
    @patch('src.api.routes.os.path.exists')
    def test_current_logfile_contents(self, mock_exists, mock_read, client, reset_state):
        """Test /current-logfile-contents endpoint."""
        test_path = "/logs/test.log"
        test_lines = ["line 1", "line 2", "line 3"]

        state.state["current_logfile"] = test_path
        mock_exists.return_value = True
        mock_read.return_value = test_lines

        response = client.get("/current-logfile-contents")

        assert response.status_code == 200
        data = response.json()
        assert data["logfile"] == test_path
        assert data["lines"] == test_lines
        mock_read.assert_called_once_with(test_path, None)

    @patch('src.api.routes.read_logfile_lines')
    @patch('src.api.routes.os.path.exists')
    def test_current_logfile_contents_with_limit(self, mock_exists, mock_read, client, reset_state):
        """Test /current-logfile-contents endpoint with line limit."""
        test_path = "/logs/test.log"
        test_lines = ["line 1", "line 2"]

        state.state["current_logfile"] = test_path
        mock_exists.return_value = True
        mock_read.return_value = test_lines

        response = client.get("/current-logfile-contents?lines=10")

        assert response.status_code == 200
        data = response.json()
        assert data["lines"] == test_lines
        mock_read.assert_called_once_with(test_path, 10)

    @patch('src.api.routes.os.path.exists')
    def test_current_logfile_contents_no_file(self, mock_exists, client, reset_state):
        """Test /current-logfile-contents when logfile doesn't exist."""
        state.state["current_logfile"] = None

        response = client.get("/current-logfile-contents")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data

    @patch('src.api.routes.get_all_log_files')
    @patch('src.api.routes.resolve_log_dir')
    def test_list_logs(self, mock_resolve, mock_get_files, client):
        """Test /logs endpoint."""
        mock_resolve.return_value = "/test/logs"
        mock_get_files.return_value = ["file1.log", "file2.log"]

        response = client.get("/logs")

        assert response.status_code == 200
        data = response.json()
        assert data["log_dir"] == "/test/logs"
        assert data["files"] == ["file1.log", "file2.log"]

    @patch('src.api.routes.read_logfile_lines')
    @patch('src.api.routes.os.path.exists')
    def test_tail_raw(self, mock_exists, mock_read, client, reset_state):
        """Test /tail endpoint."""
        test_path = "/logs/test.log"
        test_lines = ["line 1", "line 2"]

        state.state["current_logfile"] = test_path
        mock_exists.return_value = True
        mock_read.return_value = test_lines

        response = client.get("/tail")

        assert response.status_code == 200
        data = response.json()
        assert data["logfile"] == test_path
        assert data["lines"] == test_lines
        mock_read.assert_called_once_with(test_path, 50)  # Default 50 lines

    @patch('src.api.routes.read_logfile_lines')
    @patch('src.api.routes.os.path.exists')
    def test_tail_raw_custom_lines(self, mock_exists, mock_read, client, reset_state):
        """Test /tail endpoint with custom line count."""
        test_path = "/logs/test.log"
        test_lines = ["line 1"]

        state.state["current_logfile"] = test_path
        mock_exists.return_value = True
        mock_read.return_value = test_lines

        response = client.get("/tail?lines=100")

        assert response.status_code == 200
        mock_read.assert_called_once_with(test_path, 100)

    @patch('src.api.routes.os.path.exists')
    def test_tail_raw_no_file(self, mock_exists, client, reset_state):
        """Test /tail when no logfile is available."""
        state.state["current_logfile"] = None

        response = client.get("/tail")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data

    @patch('src.api.routes.VERSION', 'test-version-1.2.3')
    def test_version(self, client):
        """Test /version endpoint."""
        response = client.get("/version")

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "test-version-1.2.3"

    @patch('src.api.routes.DEBUG', True)
    def test_debug_status_enabled(self, client):
        """Test /debug endpoint when debug is enabled."""
        response = client.get("/debug")

        assert response.status_code == 200
        data = response.json()
        assert data["debug"] is True

    @patch('src.api.routes.DEBUG', False)
    def test_debug_status_disabled(self, client):
        """Test /debug endpoint when debug is disabled."""
        response = client.get("/debug")

        assert response.status_code == 200
        data = response.json()
        assert data["debug"] is False

    @patch('src.api.routes.resolve_log_dir')
    @patch('src.api.routes.VERSION', 'test-version')
    @patch('src.api.routes.DEBUG', True)
    @patch('src.api.routes.get_feature_flags')
    def test_health(self, mock_get_feature_flags, mock_resolve, client, reset_state):
        """Test /health endpoint."""
        mock_resolve.return_value = "/test/logs"
        mock_get_feature_flags.return_value = {
            "ENABLE_HARDWARE_MONITORING": True,
            "ENABLE_GPU_DEMAND_API": False,
            "ENABLE_NETWORK_MONITORING": True,
            "ENABLE_PROCESS_MONITORING": False,
        }
        state.state["current_logfile"] = "/test/logs/current.log"
        state.state["salad_active"] = True

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["monitor_running"] is True
        assert data["current_logfile"] == "/test/logs/current.log"
        assert data["log_dir"] == "/test/logs"
        assert data["version"] == "test-version"
        assert data["debug"] is True
        assert data["features"] == {
            "ENABLE_HARDWARE_MONITORING": True,
            "ENABLE_GPU_DEMAND_API": False,
            "ENABLE_NETWORK_MONITORING": True,
            "ENABLE_PROCESS_MONITORING": False,
        }
        assert "state" in data
        assert data["state"]["salad_active"] is True

    def test_health_monitor_always_running(self, client):
        """Test /health always reports monitor as running."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["monitor_running"] is True
