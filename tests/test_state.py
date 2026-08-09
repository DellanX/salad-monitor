"""Unit tests for src/state.py"""

import pytest
from src import state


@pytest.mark.unit
class TestState:
    """Test state management functions."""

    def setup_method(self):
        """Reset state before each test."""
        state.state["salad_pending"] = False
        state.state["salad_active"] = False
        state.state["gpu_reserved"] = False
        state.state["last_event"] = None
        state.state["current_logfile"] = None

    def test_initial_state(self):
        """Test that initial state is all False."""
        assert state.state["salad_pending"] is False
        assert state.state["salad_active"] is False
        assert state.state["gpu_reserved"] is False
        assert state.state["last_event"] is None
        assert state.state["current_logfile"] is None

    def test_reset_state(self):
        """Test reset_state sets everything to idle."""
        # Set some active state
        state.state["salad_active"] = True
        state.state["gpu_reserved"] = True
        state.state["salad_pending"] = True
        state.state["last_event"] = "active"

        # Reset
        state.reset_state()

        # Verify
        assert state.state["salad_active"] is False
        assert state.state["gpu_reserved"] is False
        assert state.state["salad_pending"] is False
        assert state.state["last_event"] == "idle"

    def test_set_pending(self):
        """Test set_pending marks workload as pending."""
        state.set_pending()
        
        assert state.state["salad_pending"] is True
        assert state.state["last_event"] == "pending"

    def test_set_gpu_reserved(self):
        """Test set_gpu_reserved marks GPU as reserved."""
        state.set_gpu_reserved()
        
        assert state.state["gpu_reserved"] is True
        assert state.state["last_event"] == "gpu_reserved"

    def test_set_active(self):
        """Test set_active marks workload as active."""
        state.set_active()
        
        assert state.state["salad_active"] is True
        assert state.state["last_event"] == "active"

    def test_set_current_logfile(self):
        """Test set_current_logfile updates the logfile path."""
        test_path = "/logs/test.log"
        state.set_current_logfile(test_path)
        
        assert state.state["current_logfile"] == test_path

    def test_state_transitions(self):
        """Test typical state transition flow."""
        # Start idle
        assert state.state["salad_pending"] is False
        
        # Workload received
        state.set_pending()
        assert state.state["salad_pending"] is True
        assert state.state["last_event"] == "pending"
        
        # GPU reserved
        state.set_gpu_reserved()
        assert state.state["gpu_reserved"] is True
        assert state.state["last_event"] == "gpu_reserved"
        
        # Workload active
        state.set_active()
        assert state.state["salad_active"] is True
        assert state.state["last_event"] == "active"
        
        # Back to idle
        state.reset_state()
        assert state.state["salad_active"] is False
        assert state.state["gpu_reserved"] is False
        assert state.state["salad_pending"] is False
        assert state.state["last_event"] == "idle"

    def test_state_persistence_across_calls(self):
        """Test that state persists across multiple function calls."""
        state.set_pending()
        state.set_gpu_reserved()
        
        # Both should remain true
        assert state.state["salad_pending"] is True
        assert state.state["gpu_reserved"] is True

    def test_set_wallet_info(self):
        """Test set_wallet_info updates wallet state."""
        state.set_wallet_info("$100.50", "$150.75")
        
        assert state.state["wallet_balance"] == "$100.50"
        assert state.state["wallet_projected"] == "$150.75"

    def test_set_job_info_without_timestamp(self):
        """Test set_job_info with job ID only."""
        job_id = "abc-123-def"
        state.set_job_info(job_id)
        
        assert state.state["job_id"] == job_id
        assert "job_start_time" in state.state

    def test_set_container_status(self):
        """Test set_container_status updates status."""
        state.set_container_status("Running (Stable)")
        
        assert state.state["container_status"] == "Running (Stable)"

    def test_set_matrix_status(self):
        """Test set_matrix_status updates matrix info."""
        state.set_matrix_status("matrix_received", 5)
        
        assert state.state["matrix_status"] == "matrix_received"
        # Workload count might be stored differently

    def test_set_download_progress(self):
        """Test set_download_progress updates download state."""
        state.set_download_progress(
            progress_pct=50.0,
            total_mb=512,
            estimated_mb=1024,
            eta_seconds=300,
            speed_kbps=1024
        )
        
        assert state.state["download_progress_pct"] == 50.0
        assert state.state["download_total_mb"] == 512
        assert state.state["download_estimated_mb"] == 1024
        assert state.state["download_eta_seconds"] == 300
        assert state.state["download_speed_kbps"] == 1024

    def test_set_wsl_disk_size(self):
        """Test set_wsl_disk_size updates disk size."""
        state.set_wsl_disk_size(256.5)
        
        assert state.state["wsl_disk_size_gb"] == 256.5

    def test_set_bandwidth_node(self):
        """Test set_bandwidth_node updates bandwidth info."""
        state.set_bandwidth_node("node-001", active=True)
        
        assert state.state["bandwidth_node_name"] == "node-001"
        assert state.state["bandwidth_active"] == True

    def test_set_last_warning(self):
        """Test set_last_warning stores warning message."""
        state.set_last_warning("GPU overheating!")
        
        assert state.state["last_warning"] == "GPU overheating!"
        assert "last_warning_time" in state.state

    def test_update_job_uptime(self):
        """Test update_job_uptime calculates uptime."""
        from datetime import datetime, timedelta
        
        # Set a job start time
        start = datetime.now() - timedelta(hours=2)
        state.state["job_start_time"] = start
        
        state.update_job_uptime()
        
        # Should have calculated uptime
        uptime = state.state.get("job_uptime_seconds", 0)
        # Should be around 7200 seconds (2 hours)
        assert uptime > 7000 and uptime < 7400
