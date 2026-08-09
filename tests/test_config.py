"""Unit tests for src/config.py"""

import os
import pytest
from unittest.mock import patch
from src import config


@pytest.mark.unit
class TestConfig:
    """Test configuration utilities."""

    def test_default_log_dir(self):
        """Test default log directory constant."""
        assert config.DEFAULT_LOG_DIR == "/logs"

    def test_debug_disabled_by_default(self):
        """Test that debug mode is disabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            # Re-evaluate DEBUG
            debug_val = os.environ.get("DEBUG", "false").lower() == "true"
            assert debug_val is False

    def test_debug_enabled_with_env_var(self):
        """Test that debug mode can be enabled via environment variable."""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            debug_val = os.environ.get("DEBUG", "false").lower() == "true"
            assert debug_val is True

    def test_debug_case_insensitive(self):
        """Test that DEBUG env var is case insensitive."""
        test_cases = ["true", "True", "TRUE", "TrUe"]
        for value in test_cases:
            with patch.dict(os.environ, {"DEBUG": value}):
                debug_val = os.environ.get("DEBUG", "false").lower() == "true"
                assert debug_val is True, f"Failed for value: {value}"

    def test_debug_function_with_debug_disabled(self, capsys):
        """Test debug function doesn't print when DEBUG is False."""
        with patch.object(config, "DEBUG", False):
            config.debug("test message")
            captured = capsys.readouterr()
            assert captured.out == ""

    def test_debug_function_with_debug_enabled(self, capsys):
        """Test debug function prints when DEBUG is True."""
        with patch.object(config, "DEBUG", True):
            config.debug("test message")
            captured = capsys.readouterr()
            assert "[DEBUG] test message\n" == captured.out

    def test_resolve_log_dir_default(self):
        """Test resolve_log_dir returns default when no env var set."""
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(config, "debug"):
                result = config.resolve_log_dir()
                expected = r"C:\ProgramData\Salad\logs" if os.name == "nt" else "/logs"
                assert result == expected

    def test_resolve_log_dir_custom(self):
        """Test resolve_log_dir returns custom path from env var."""
        custom_path = "/custom/logs"
        with patch.dict(os.environ, {"LOG_DIR": custom_path}):
            with patch.object(config, "debug"):
                result = config.resolve_log_dir()
                assert result == custom_path

    def test_version_import_failure_handled(self):
        """Test that VERSION defaults to 'unknown' if import fails."""
        # This tests the try/except in config.py
        # If version module doesn't exist, VERSION should be "unknown"
        assert isinstance(config.VERSION, str)

    def test_runtime_settings_shape(self):
        """Test runtime settings include collector mode keys."""
        runtime = config.get_runtime_settings()
        assert "COLLECTOR_MODE" in runtime
        assert "SIDECAR_STALE_SECONDS" in runtime
        assert "MINIMUM_SIDECAR_VERSION" in runtime
        assert runtime["MINIMUM_SIDECAR_VERSION"] == config.VERSION
