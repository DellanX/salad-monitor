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

    def test_monitor_state_type(self):
        """Test MonitorState TypedDict structure."""
        # Verify core expected keys exist (state may have additional monitoring fields)
        required_keys = {
            "salad_pending",
            "salad_active",
            "gpu_reserved",
            "last_event",
            "current_logfile"
        }
        actual_keys = set(state.state.keys())
        assert required_keys.issubset(actual_keys), f"Missing required keys: {required_keys - actual_keys}"
