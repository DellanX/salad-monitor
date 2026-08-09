"""Unit tests for src/monitor.py"""

import pytest
from unittest.mock import patch, MagicMock, call
from src import monitor, state


@pytest.mark.unit
class TestMonitor:
    """Test main monitoring loop."""

    def setup_method(self):
        """Reset state before each test."""
        state.state["salad_pending"] = False
        state.state["salad_active"] = False
        state.state["gpu_reserved"] = False
        state.state["last_event"] = None
        state.state["current_logfile"] = None

    @patch('src.monitor.time.sleep')
    @patch('src.monitor.resolve_log_dir')
    @patch('src.monitor.get_latest_log_file')
    def test_monitor_logs_no_files(self, mock_get_latest, mock_resolve, mock_sleep):
        """Test monitor when no log files are available."""
        mock_resolve.return_value = "/logs"
        mock_get_latest.return_value = None
        
        # Make sleep raise exception to break loop
        mock_sleep.side_effect = [None, KeyboardInterrupt]
        
        with patch('src.monitor.debug'):
            with pytest.raises(KeyboardInterrupt):
                monitor.monitor_logs()
        
        # Should have slept when no files found
        assert mock_sleep.call_count >= 1

    @patch('src.monitor.time.sleep')
    @patch('src.monitor.parse_line')
    @patch('src.monitor.tail_file')
    @patch('src.monitor.get_latest_log_file')
    @patch('src.monitor.resolve_log_dir')
    def test_monitor_logs_with_file(self, mock_resolve, mock_get_latest, mock_tail, mock_parse, mock_sleep):
        """Test monitor detects and sets current logfile."""
        mock_resolve.return_value = "/logs"
        mock_get_latest.side_effect = ["/logs/log-001.txt", KeyboardInterrupt]
        mock_tail.return_value = iter(["line 1\n", "line 2\n"])
        
        with patch('src.monitor.debug'):
            with pytest.raises(KeyboardInterrupt):
                monitor.monitor_logs()
        
        # Should have set current logfile
        assert state.state["current_logfile"] == "/logs/log-001.txt"

    @patch('src.monitor.time.sleep')
    @patch('src.monitor.parse_line')
    @patch('src.monitor.tail_file')
    @patch('src.monitor.get_latest_log_file')
    @patch('src.monitor.resolve_log_dir')
    def test_monitor_logs_parses_lines(self, mock_resolve, mock_get_latest, mock_tail, mock_parse, mock_sleep):
        """Test monitor calls parse_line for each log line."""
        mock_resolve.return_value = "/logs"
        mock_get_latest.side_effect = ["/logs/log-001.txt", KeyboardInterrupt]
        test_lines = ["INFO: Workload received\n", "INFO: GPU HardwareCompatibility\n"]
        mock_tail.return_value = iter(test_lines)
        
        with patch('src.monitor.debug'):
            with pytest.raises(KeyboardInterrupt):
                monitor.monitor_logs()
        
        # parse_line should be called for each line
        assert mock_parse.call_count == 2
        for i, line in enumerate(test_lines):
            assert mock_parse.call_args_list[i] == call(line)

    @patch('src.monitor.time.sleep')
    @patch('src.monitor.get_latest_log_file')
    @patch('src.monitor.resolve_log_dir')
    def test_monitor_logs_switches_files(self, mock_resolve, mock_get_latest, mock_sleep):
        """Test monitor switches to new log file when it changes."""
        mock_resolve.return_value = "/logs"
        # Return different files on successive calls
        mock_get_latest.side_effect = [
            "/logs/log-001.txt",
            "/logs/log-001.txt",
            "/logs/log-002.txt",
            KeyboardInterrupt
        ]
        
        with patch('src.monitor.tail_file') as mock_tail:
            mock_tail.return_value = iter([])
            with patch('src.monitor.debug'):
                with pytest.raises(KeyboardInterrupt):
                    monitor.monitor_logs()
        
        # Should have switched from log-001 to log-002
        assert state.state["current_logfile"] == "/logs/log-002.txt"

    @patch('src.monitor.time.sleep')
    @patch('src.monitor.get_latest_log_file')
    @patch('src.monitor.resolve_log_dir')
    def test_monitor_logs_loop_counter(self, mock_resolve, mock_get_latest, mock_sleep):
        """Test that loop counter increments for monitoring updates."""
        mock_resolve.return_value = "/logs"
        # Simulate several loop iterations
        call_count = [0]
        
        def get_latest_side_effect():
            call_count[0] += 1
            if call_count[0] >= 4:
                raise KeyboardInterrupt
            return "/logs/log-001.txt"
        
        mock_get_latest.side_effect = get_latest_side_effect
        
        with patch('src.monitor.tail_file') as mock_tail:
            mock_tail.return_value = iter([])
            with patch('src.monitor.debug'):
                with pytest.raises(KeyboardInterrupt):
                    monitor.monitor_logs()
        
        # Should have iterated at least 3 times
        assert call_count[0] >= 3

    @patch('src.monitor.time.sleep')
    @patch('src.monitor.get_latest_log_file')
    @patch('src.monitor.resolve_log_dir')
    def test_monitor_logs_handles_tail_exception(self, mock_resolve, mock_get_latest, mock_sleep):
        """Test monitor handles exceptions from tail_file gracefully."""
        mock_resolve.return_value = "/logs"
        mock_get_latest.side_effect = ["/logs/log-001.txt", KeyboardInterrupt]
        
        with patch('src.monitor.tail_file') as mock_tail:
            mock_tail.side_effect = IOError("File error")
            with patch('src.monitor.debug'):
                # Should raise the IOError from tail_file
                with pytest.raises(IOError):
                    monitor.monitor_logs()

    @patch('src.monitor.time.sleep')
    @patch('src.monitor.resolve_log_dir')
    @patch('src.monitor.get_latest_log_file')
    def test_monitor_initialization(self, mock_get_latest, mock_resolve, mock_sleep):
        """Test that monitor initializes correctly with features."""
        mock_resolve.return_value = "/logs"
        mock_get_latest.return_value = None
        mock_sleep.side_effect = KeyboardInterrupt
        
        with patch('src.monitor.debug') as mock_debug:
            with pytest.raises(KeyboardInterrupt):
                monitor.monitor_logs()
            
            # Should have logged initialization
            debug_calls = [str(call) for call in mock_debug.call_args_list]
            init_logs = [c for c in debug_calls if "watching directory" in c.lower()]
            assert len(init_logs) > 0

    def test_monitor_feature_flags(self):
        """Test that monitor correctly sets feature availability flags."""
        # These should be set based on imports
        assert isinstance(monitor.HARDWARE_AVAILABLE, bool)
        assert isinstance(monitor.NETWORK_AVAILABLE, bool)
        assert isinstance(monitor.PROCESSES_AVAILABLE, bool)
        assert isinstance(monitor.GPU_DEMAND_AVAILABLE, bool)

    @patch('src.monitor.time.sleep')
    @patch('src.monitor.get_latest_log_file')
    @patch('src.monitor.resolve_log_dir')
    def test_monitor_catches_monitoring_exceptions(self, mock_resolve, mock_get_latest, mock_sleep):
        """Test that monitor catches exceptions from monitoring functions."""
        mock_resolve.return_value = "/logs"
        mock_get_latest.side_effect = ["/logs/log-001.txt", "/logs/log-001.txt", KeyboardInterrupt]
        
        with patch('src.monitor.tail_file') as mock_tail:
            mock_tail.return_value = iter([])
            
            # Mock monitoring functions to raise
            with patch('src.monitor.HARDWARE_AVAILABLE', True):
                with patch('src.monitor.update_all_hardware') as mock_hw:
                    mock_hw.side_effect = RuntimeError("HW Error")
                    
                    with patch('src.monitor.debug'):
                        # Should not raise, should catch and log
                        with pytest.raises(KeyboardInterrupt):
                            monitor.monitor_logs()
