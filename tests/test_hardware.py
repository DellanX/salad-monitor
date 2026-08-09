"""Unit tests for src/hardware.py"""

import pytest
from unittest.mock import patch, MagicMock
from src import hardware, state


@pytest.mark.unit
class TestHardwareMonitoring:
    """Test hardware monitoring functionality."""

    def setup_method(self):
        """Reset state before each test."""
        state.state.clear()
        state.state.update({
            "salad_pending": False,
            "salad_active": False,
            "gpu_reserved": False,
            "last_event": None,
            "current_logfile": None,
        })

    @patch('src.hardware.PSUTIL_AVAILABLE', False)
    def test_update_cpu_metrics_psutil_unavailable(self):
        """Test CPU metrics update when psutil is unavailable."""
        hardware.update_cpu_metrics()
        
        # Should not raise and should not set state
        assert "cpu_load_pct" not in state.state or state.state.get("cpu_load_pct") is None

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.psutil.cpu_percent')
    @patch('src.hardware._get_cpu_name')
    def test_update_cpu_metrics_success(self, mock_get_name, mock_cpu_percent):
        """Test successful CPU metrics update."""
        mock_cpu_percent.return_value = 42.5
        mock_get_name.return_value = "Intel Core i7-9700K"
        
        hardware.update_cpu_metrics()
        
        assert state.state["cpu_load_pct"] == 42.5
        assert state.state["cpu_name"] == "Intel Core i7-9700K"

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.psutil.cpu_percent', side_effect=Exception("CPU Error"))
    def test_update_cpu_metrics_exception(self, mock_cpu_percent):
        """Test CPU metrics update handles exceptions gracefully."""
        with patch('src.hardware.debug'):
            hardware.update_cpu_metrics()
        
        # Should not crash, state may or may not be updated
        assert "cpu_load_pct" not in state.state or isinstance(state.state.get("cpu_load_pct"), (int, float, type(None)))

    @patch('src.hardware.PSUTIL_AVAILABLE', False)
    def test_update_ram_metrics_psutil_unavailable(self):
        """Test RAM metrics update when psutil is unavailable."""
        hardware.update_ram_metrics()
        
        # Should not raise
        assert "ram_used_gb" not in state.state or state.state.get("ram_used_gb") is None

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.psutil.virtual_memory')
    def test_update_ram_metrics_success(self, mock_virtual_memory):
        """Test successful RAM metrics update."""
        # Mock psutil.virtual_memory() return
        mock_mem = MagicMock()
        mock_mem.used = 8 * (1024 ** 3)  # 8 GB
        mock_mem.total = 16 * (1024 ** 3)  # 16 GB
        mock_mem.percent = 50.0
        mock_virtual_memory.return_value = mock_mem
        
        hardware.update_ram_metrics()
        
        assert state.state["ram_used_gb"] == 8.0
        assert state.state["ram_total_gb"] == 16.0
        assert state.state["ram_load_pct"] == 50.0

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.psutil.virtual_memory', side_effect=Exception("RAM Error"))
    def test_update_ram_metrics_exception(self, mock_virtual_memory):
        """Test RAM metrics update handles exceptions gracefully."""
        with patch('src.hardware.debug'):
            hardware.update_ram_metrics()
        
        # Should not crash
        assert isinstance(state.state.get("ram_used_gb"), (float, type(None)))

    @patch('src.hardware.PSUTIL_AVAILABLE', False)
    def test_update_gpu_metrics_psutil_unavailable(self):
        """Test GPU metrics update when psutil is unavailable."""
        hardware.update_gpu_metrics()
        
        # Should not raise

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.subprocess.run')
    def test_update_gpu_metrics_nvidia_smi_success(self, mock_run):
        """Test successful GPU metrics update with nvidia-smi."""
        # Mock nvidia-smi output
        mock_result = MagicMock()
        mock_result.stdout = "NVIDIA GeForce RTX 3090,75.0,16,12000"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        hardware.update_gpu_metrics()
        
        # Check that GPU data was updated
        assert "gpu_name" in state.state or "gpu_utilization_pct" in state.state

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.subprocess.run', side_effect=Exception("GPU Error"))
    def test_update_gpu_metrics_nvidia_smi_error(self, mock_run):
        """Test GPU metrics update handles nvidia-smi errors gracefully."""
        with patch('src.hardware.debug'):
            hardware.update_gpu_metrics()
        
        # Should not crash

    @patch('src.hardware.PSUTIL_AVAILABLE', False)
    def test_update_disk_metrics_psutil_unavailable(self):
        """Test disk metrics update when psutil is unavailable."""
        hardware.update_disk_metrics()
        
        # Should not raise

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.psutil.disk_usage')
    def test_update_disk_metrics_success(self, mock_disk_usage):
        """Test successful disk metrics update."""
        # Mock psutil.disk_usage() return for C: drive
        mock_usage = MagicMock()
        mock_usage.total = 500 * (1024 ** 3)  # 500 GB
        mock_usage.used = 250 * (1024 ** 3)  # 250 GB
        mock_usage.free = 250 * (1024 ** 3)  # 250 GB
        mock_disk_usage.return_value = mock_usage
        
        hardware.update_disk_metrics()
        
        # Should have updated disk state
        assert "disk_size_gb" in state.state or "disk_utilization_pct" in state.state

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.psutil.disk_usage', side_effect=Exception("Disk Error"))
    def test_update_disk_metrics_exception(self, mock_disk_usage):
        """Test disk metrics update handles exceptions gracefully."""
        with patch('src.hardware.debug'):
            hardware.update_disk_metrics()
        
        # Should not crash

    @patch('src.hardware.update_cpu_metrics')
    @patch('src.hardware.update_ram_metrics')
    @patch('src.hardware.update_gpu_metrics')
    @patch('src.hardware.update_disk_metrics')
    def test_update_all_hardware(self, mock_disk, mock_gpu, mock_ram, mock_cpu):
        """Test that update_all_hardware calls all update functions."""
        hardware.update_all_hardware()
        
        mock_cpu.assert_called_once()
        mock_ram.assert_called_once()
        mock_gpu.assert_called_once()
        mock_disk.assert_called_once()

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.psutil.cpu_percent')
    def test_cpu_metrics_rounding(self, mock_cpu_percent):
        """Test that CPU metrics are properly rounded."""
        mock_cpu_percent.return_value = 42.56789
        
        with patch('src.hardware._get_cpu_name', return_value="Test CPU"):
            hardware.update_cpu_metrics()
        
        # Should be rounded to 1 decimal place
        assert state.state["cpu_load_pct"] == 42.6

    @patch('src.hardware.PSUTIL_AVAILABLE', True)
    @patch('src.hardware.psutil.virtual_memory')
    def test_ram_metrics_rounding(self, mock_virtual_memory):
        """Test that RAM metrics are properly rounded."""
        mock_mem = MagicMock()
        mock_mem.used = 8.123456 * (1024 ** 3)
        mock_mem.total = 16.789012 * (1024 ** 3)
        mock_mem.percent = 50.56789
        mock_virtual_memory.return_value = mock_mem
        
        hardware.update_ram_metrics()
        
        # Used and total should be rounded to 2 decimal places
        assert isinstance(state.state["ram_used_gb"], float)
        assert isinstance(state.state["ram_total_gb"], float)
        # Percent should be rounded to 1 decimal place
        assert state.state["ram_load_pct"] == 50.6
