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

    def test_parse_line_matrix_status(self):
        """Test parsing matrix status from log line."""
        log_parser.parse_line("INFO: Received desired state from matrix - 3 workloads")
        
        assert state.state["matrix_status"] == "matrix_received"

    def test_parse_line_wallet_info(self):
        """Test parsing wallet information."""
        log_parser.parse_line("Wallet: Current($100.50), Predicted($200.75)")
        
        assert state.state["wallet_balance"] == "$100.50"
        assert state.state["wallet_projected"] == "$200.75"

    def test_parse_line_job_id(self):
        """Test parsing job ID from log line."""
        log_parser.parse_line("New job: salad.com/sce/abc-def-123-456")
        
        assert state.state["job_id"] == "abc-def-123-456"
        assert state.state["container_status"] == "Starting..."

    def test_parse_line_layer_progress(self):
        """Test parsing layer download progress."""
        log_parser.parse_line("Pull progress event: layer@sha256:abcd1234 99.5")
        
        assert state.state["download_active_layer"] == "abcd1234"
        assert state.state["download_layer_progress"] == 9950.0  # 99.5 * 100

    def test_parse_line_global_progress(self):
        """Test parsing global download progress."""
        # Set up preconditions
        state.state["download_total_mb"] = 100.0
        
        log_parser.parse_line("Progress(0.50)")
        
        assert state.state["download_progress_pct"] == 50.0

    def test_parse_line_container_running(self):
        """Test parsing container running status."""
        log_parser.parse_line("Container status: Running(Ready)")
        
        assert state.state["container_status"] == "Running (Stable)"

    def test_extract_timestamp(self):
        """Test timestamp extraction from log line."""
        line = "2024-01-15 14:30:45 INFO: Some message"
        timestamp = log_parser._extract_timestamp(line)
        
        assert timestamp is not None
        assert timestamp.year == 2024
        assert timestamp.month == 1
        assert timestamp.day == 15
        assert timestamp.hour == 14
        assert timestamp.minute == 30
        assert timestamp.second == 45

    def test_extract_timestamp_invalid(self):
        """Test timestamp extraction with invalid format."""
        line = "No timestamp here"
        timestamp = log_parser._extract_timestamp(line)
        
        assert timestamp is None

    def test_extract_timestamp_malformed(self):
        """Test timestamp extraction with malformed date."""
        line = "2024-13-45 99:99:99 Invalid date"
        timestamp = log_parser._extract_timestamp(line)
        
        assert timestamp is None

    def test_parse_line_new_job_resets_download(self):
        """Test that new job resets download progress tracking."""
        # Set download state
        state.state["download_progress_pct"] = 50.0
        state.state["download_total_mb"] = 500.0
        state.state["is_downloading"] = True
        
        # Parse new job
        log_parser.parse_line("New job: salad.com/sce/new-job-id-123")
        
        # Should be reset
        assert state.state["is_downloading"] == False
        assert state.state["download_progress_pct"] is None
        assert state.state["download_total_mb"] == 0.0

    def test_parse_line_progress_with_speed(self):
        """Test download progress with speed calculation."""
        state.state["download_total_mb"] = 100.0
        state.state["vnet_rx_kbps"] = 1024.0
        
        log_parser.parse_line("Progress(0.75)")
        
        assert state.state["download_progress_pct"] == 75.0
        assert state.state["download_speed_kbps"] == 1024.0

    def test_parse_line_layer_progress_with_comma(self):
        """Test layer progress parsing with comma decimal separator."""
        log_parser.parse_line("Pull progress event: layer@sha256:ef123456 99,9")
        
        assert state.state["download_layer_progress"] == 9990.0  # 99.9 * 100

    def test_parse_multiple_patterns_same_line(self):
        """Test parsing line with multiple patterns."""
        log_parser.parse_line("Wallet: Current($50), Predicted($100) and Progress(0.25)")
        
        assert state.state["wallet_balance"] == "$50"
        assert state.state["wallet_projected"] == "$100"
        assert state.state["download_progress_pct"] == 25.0

    def test_parse_line_already_installed(self):
        """Test parsing 'already installed' container status."""
        log_parser.parse_line("Container already installed and running")
        
        assert state.state["container_status"] == "Running (Stable)"

    def test_parse_line_already_running(self):
        """Test parsing 'already running' container status."""
        log_parser.parse_line("Workload is already running")
        
        assert state.state["container_status"] == "Running (Stable)"
