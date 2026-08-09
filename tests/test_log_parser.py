"""Unit tests for src/log_parser.py"""

import pytest
from unittest.mock import patch, MagicMock
from src import log_parser, state


@pytest.mark.unit
class TestLogParser:
    """Test log line parsing logic."""

    def setup_method(self):
        """Reset state before each test."""
        state.state["salad_pending"] = False
        state.state["salad_active"] = False
        state.state["gpu_reserved"] = False
        state.state["last_event"] = None

    def test_parse_line_workload_received(self):
        """Test parsing 'workload received' event."""
        log_parser.parse_line("INFO: Workload received from server")
        
        assert state.state["salad_pending"] is True
        assert state.state["last_event"] == "pending"

    def test_parse_line_planned_actions(self):
        """Test parsing 'planned actions' event."""
        log_parser.parse_line("DEBUG: Planned actions for workload")
        
        assert state.state["salad_pending"] is True
        assert state.state["last_event"] == "pending"

    def test_parse_line_request_install(self):
        """Test parsing 'requestinstall' event."""
        log_parser.parse_line("INFO: RequestInstall command received")
        
        assert state.state["salad_pending"] is True
        assert state.state["last_event"] == "pending"

    def test_parse_line_gpu_hardware_compatibility(self):
        """Test parsing GPU hardware compatibility event."""
        log_parser.parse_line("INFO: GPU HardwareCompatibility check passed")
        
        assert state.state["gpu_reserved"] is True
        assert state.state["last_event"] == "gpu_reserved"

    def test_parse_line_already_running(self):
        """Test parsing 'is already running' event."""
        log_parser.parse_line("INFO: Workload is already running")
        
        assert state.state["salad_active"] is True
        assert state.state["last_event"] == "active"

    def test_parse_line_starting_workload(self):
        """Test parsing 'starting workload' event."""
        log_parser.parse_line("INFO: Starting workload container")
        
        assert state.state["salad_active"] is True
        assert state.state["last_event"] == "active"

    def test_parse_line_workload_completed(self):
        """Test parsing 'workload completed' event."""
        # First set some active state
        state.state["salad_active"] = True
        state.state["gpu_reserved"] = True
        state.state["salad_pending"] = True
        
        # Then parse completion
        log_parser.parse_line("INFO: Workload completed successfully")
        
        assert state.state["salad_active"] is False
        assert state.state["gpu_reserved"] is False
        assert state.state["salad_pending"] is False
        assert state.state["last_event"] == "idle"

    def test_parse_line_releasing_gpu(self):
        """Test parsing 'releasing gpu' event."""
        # First set some active state
        state.state["salad_active"] = True
        state.state["gpu_reserved"] = True
        
        # Then parse release
        log_parser.parse_line("INFO: Releasing GPU resources")
        
        assert state.state["salad_active"] is False
        assert state.state["gpu_reserved"] is False
        assert state.state["last_event"] == "idle"

    def test_parse_line_case_insensitive(self):
        """Test that parsing is case insensitive."""
        # Test uppercase
        log_parser.parse_line("INFO: WORKLOAD RECEIVED")
        assert state.state["salad_pending"] is True
        
        # Reset
        state.state["salad_pending"] = False
        
        # Test mixed case
        log_parser.parse_line("INFO: WoRkLoAd ReCeIvEd")
        assert state.state["salad_pending"] is True

    def test_parse_line_no_match(self):
        """Test parsing line with no matching patterns."""
        initial_state = state.state.copy()
        
        log_parser.parse_line("INFO: Some random log message")
        
        # State should not change
        assert state.state == initial_state

    def test_parse_line_empty_string(self):
        """Test parsing empty string doesn't crash."""
        initial_state = state.state.copy()
        
        log_parser.parse_line("")
        
        # State should not change
        assert state.state == initial_state

    def test_parse_line_whitespace(self):
        """Test parsing whitespace doesn't crash."""
        initial_state = state.state.copy()
        
        log_parser.parse_line("   \n\t  ")
        
        # State should not change
        assert state.state == initial_state

    @patch('src.log_parser.debug')
    def test_parse_line_debug_output(self, mock_debug):
        """Test that debug function is called during parsing."""
        log_parser.parse_line("INFO: Workload received")
        
        # Should have called debug at least once
        assert mock_debug.call_count >= 1

    def test_multiple_events_in_sequence(self):
        """Test parsing multiple events in sequence."""
        # Pending
        log_parser.parse_line("INFO: Workload received")
        assert state.state["last_event"] == "pending"
        
        # GPU Reserved
        log_parser.parse_line("INFO: GPU HardwareCompatibility check")
        assert state.state["last_event"] == "gpu_reserved"
        
        # Active
        log_parser.parse_line("INFO: Starting workload")
        assert state.state["last_event"] == "active"
        
        # Completed
        log_parser.parse_line("INFO: Workload completed")
        assert state.state["last_event"] == "idle"

    def test_parse_line_with_surrounding_text(self):
        """Test that patterns are detected even with surrounding text."""
        log_parser.parse_line(
            "2024-01-01 12:00:00 [INFO] Container workload received from scheduler"
        )
        assert state.state["salad_pending"] is True

    def test_parse_line_partial_matches_ignored(self):
        """Test that partial keyword matches don't trigger false positives."""
        # These should NOT trigger state changes
        initial_state = state.state.copy()
        
        # Not "workload received" but similar
        log_parser.parse_line("INFO: workflow received")
        log_parser.parse_line("INFO: workload rejected")
        
        assert state.state == initial_state
