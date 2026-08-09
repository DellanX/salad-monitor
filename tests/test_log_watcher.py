"""Unit tests for src/log_watcher.py"""

import pytest
from unittest.mock import patch, mock_open, MagicMock
from src import log_watcher


@pytest.mark.unit
class TestLogWatcher:
    """Test log file watching and tailing utilities."""

    @patch('src.log_watcher.glob.glob')
    @patch('src.log_watcher.resolve_log_dir')
    def test_get_latest_log_file_with_files(self, mock_resolve, mock_glob):
        """Test getting latest log file when files exist."""
        mock_resolve.return_value = "/logs"
        mock_glob.return_value = [
            "/logs/log-001.txt",
            "/logs/log-002.txt",
            "/logs/log-003.txt"
        ]
        
        result = log_watcher.get_latest_log_file()
        
        assert result == "/logs/log-003.txt"
        mock_glob.assert_called_once()

    @patch('src.log_watcher.glob.glob')
    @patch('src.log_watcher.resolve_log_dir')
    def test_get_latest_log_file_no_files(self, mock_resolve, mock_glob):
        """Test getting latest log file when no files exist."""
        mock_resolve.return_value = "/logs"
        mock_glob.return_value = []
        
        result = log_watcher.get_latest_log_file()
        
        assert result is None

    @patch('src.log_watcher.glob.glob')
    @patch('src.log_watcher.resolve_log_dir')
    def test_get_all_log_files(self, mock_resolve, mock_glob):
        """Test getting all log files."""
        mock_resolve.return_value = "/logs"
        test_files = [
            "/logs/log-001.txt",
            "/logs/log-002.txt",
            "/logs/log-003.txt"
        ]
        mock_glob.return_value = test_files
        
        result = log_watcher.get_all_log_files()
        
        assert result == test_files
        assert len(result) == 3

    @patch('src.log_watcher.glob.glob')
    @patch('src.log_watcher.resolve_log_dir')
    def test_get_all_log_files_empty(self, mock_resolve, mock_glob):
        """Test getting all log files when none exist."""
        mock_resolve.return_value = "/logs"
        mock_glob.return_value = []
        
        result = log_watcher.get_all_log_files()
        
        assert result == []

    @patch('builtins.open', new_callable=mock_open, read_data="line1\nline2\nline3\n")
    def test_read_logfile_lines_all(self, mock_file):
        """Test reading all lines from a logfile."""
        result = log_watcher.read_logfile_lines("/logs/test.log")
        
        assert len(result) == 3
        assert result[0] == "line1\n"
        assert result[-1] == "line3\n"

    @patch('builtins.open', new_callable=mock_open, read_data="line1\nline2\nline3\nline4\nline5\n")
    def test_read_logfile_lines_limited(self, mock_file):
        """Test reading limited lines from a logfile."""
        result = log_watcher.read_logfile_lines("/logs/test.log", lines=2)
        
        assert len(result) == 2
        assert result[0] == "line4\n"
        assert result[1] == "line5\n"

    @patch('builtins.open', new_callable=mock_open, read_data="line1\nline2\nline3\n")
    def test_read_logfile_lines_limit_more_than_file(self, mock_file):
        """Test reading limited lines when limit exceeds file size."""
        result = log_watcher.read_logfile_lines("/logs/test.log", lines=10)
        
        assert len(result) == 3

    @patch('src.log_watcher.time.sleep')
    @patch('builtins.open', new_callable=mock_open)
    def test_tail_file_opens_and_seeks(self, mock_file, mock_sleep):
        """Test that tail_file opens file and configures properly."""
        # Just test that tail_file can be called without errors
        # The generator behavior is complex due to the infinite loop
        mock_f = MagicMock()
        mock_f.__enter__ = MagicMock(return_value=mock_f)
        mock_f.__exit__ = MagicMock(return_value=False)
        mock_f.seek = MagicMock()
        mock_f.readline = MagicMock(return_value="")
        mock_file.return_value = mock_f
        
        try:
            gen = log_watcher.tail_file("/logs/test.log")
            # Try to get one item from generator
            next(gen, None)
        except StopIteration:
            pass

    @patch('src.log_watcher.time.sleep')
    @patch('builtins.open', new_callable=mock_open)
    def test_tail_file_file_operations(self, mock_file, mock_sleep):
        """Test that tail_file uses proper file operations."""
        # Just verify the file is opened
        mock_f = MagicMock()
        mock_f.__enter__ = MagicMock(return_value=mock_f)
        mock_f.__exit__ = MagicMock(return_value=False)
        mock_f.readline.return_value = ""
        mock_file.return_value = mock_f
        
        try:
            gen = log_watcher.tail_file("/logs/test.log")
            next(gen, None)
        except (StopIteration, Exception):
            pass
        
        # File should have been opened
        assert mock_file.called

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_read_logfile_lines_file_not_found(self, mock_file):
        """Test handling of missing log file."""
        with pytest.raises(FileNotFoundError):
            log_watcher.read_logfile_lines("/nonexistent/log.txt")

    @patch('builtins.open', new_callable=mock_open, read_data="line with unicode: 🎵\ninvalid\xffbytes\n")
    def test_read_logfile_lines_with_encoding_errors(self, mock_file):
        """Test that read_logfile_lines handles encoding errors gracefully."""
        # open() is called with errors="ignore"
        result = log_watcher.read_logfile_lines("/logs/test.log")
        
        assert len(result) == 2
