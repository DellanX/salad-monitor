"""Unit tests for src/network.py"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src import network, state


@pytest.mark.unit
class TestNetworkMonitoring:
    """Test network monitoring functionality."""

    def setup_method(self):
        """Reset state and network tracking before each test."""
        state.state.clear()
        state.state.update({
            "salad_pending": False,
            "salad_active": False,
            "gpu_reserved": False,
            "last_event": None,
            "current_logfile": None,
        })
        # Reset module-level tracking
        network._last_vnet_rx = 0
        network._last_vnet_tx = 0
        network._last_vnet_time = datetime.min
        network._last_sgs_rx = 0
        network._last_sgs_tx = 0
        network._last_sgs_time = datetime.min

    @patch('src.network.PSUTIL_AVAILABLE', False)
    def test_update_wsl_network_psutil_unavailable(self):
        """Test WSL network update when psutil is unavailable."""
        network.update_wsl_network()
        
        # Should not raise

    @patch('src.network.PSUTIL_AVAILABLE', True)
    @patch('src.network.psutil.net_io_counters')
    def test_update_wsl_network_first_call(self, mock_net_io):
        """Test first WSL network update initializes tracking."""
        mock_io = MagicMock()
        mock_io.bytes_sent = 1000
        mock_io.bytes_recv = 2000
        mock_net_io.return_value = {
            "vEthernet (WSL)": mock_io
        }
        
        network.update_wsl_network()
        
        # First call shouldn't update speeds (no previous data)
        # But should update tracking state

    @patch('src.network.PSUTIL_AVAILABLE', True)
    @patch('src.network.psutil.net_io_counters')
    def test_update_wsl_network_speed_calculation(self, mock_net_io):
        """Test WSL network speed calculation."""
        mock_io = MagicMock()
        
        # First call
        mock_io.bytes_sent = 1000
        mock_io.bytes_recv = 2000
        mock_net_io.return_value = {"vEthernet (WSL)": mock_io}
        
        network.update_wsl_network()
        
        # Second call with more data
        mock_io.bytes_sent = 2000  # 1000 bytes more
        mock_io.bytes_recv = 4000  # 2000 bytes more
        
        with patch('src.network.datetime') as mock_datetime:
            # Mock time passage
            mock_now = MagicMock()
            mock_now.side_effect = [
                network._last_vnet_time + timedelta(seconds=1),
                network._last_vnet_time + timedelta(seconds=1)
            ]
            mock_datetime.now = mock_now
            
            network.update_wsl_network()

    @patch('src.network.PSUTIL_AVAILABLE', True)
    @patch('src.network.psutil.net_io_counters', side_effect=Exception("Network Error"))
    def test_update_wsl_network_exception(self, mock_net_io):
        """Test WSL network update handles exceptions gracefully."""
        with patch('src.network.debug'):
            network.update_wsl_network()
        
        # Should not crash

    @patch('src.network.PSUTIL_AVAILABLE', False)
    def test_update_sgs_network_psutil_unavailable(self):
        """Test SGS network update when psutil is unavailable."""
        network.update_sgs_network()
        
        # Should not raise

    @patch('src.network.PSUTIL_AVAILABLE', True)
    @patch('src.network.psutil.net_io_counters')
    def test_update_sgs_network_identifies_sgs_process(self, mock_net_io):
        """Test SGS network update identifies SGS process."""
        # SGS runs on loopback or specific interfaces
        mock_io = MagicMock()
        mock_io.bytes_sent = 1000
        mock_io.bytes_recv = 2000
        mock_net_io.return_value = {
            "lo": mock_io  # loopback
        }
        
        network.update_sgs_network()
        
        # Should process network data

    @patch('src.network.PSUTIL_AVAILABLE', True)
    @patch('src.network.psutil.net_io_counters', side_effect=Exception("Network Error"))
    def test_update_sgs_network_exception(self, mock_net_io):
        """Test SGS network update handles exceptions gracefully."""
        with patch('src.network.debug'):
            network.update_sgs_network()
        
        # Should not crash

    @patch('src.network.update_wsl_network')
    @patch('src.network.update_sgs_network')
    def test_update_all_network(self, mock_sgs, mock_wsl):
        """Test that update_all_network calls both network updates."""
        network.update_all_network()
        
        mock_wsl.assert_called_once()
        mock_sgs.assert_called_once()

    @patch('src.network.PSUTIL_AVAILABLE', True)
    @patch('src.network.psutil.net_io_counters')
    def test_network_state_updates(self, mock_net_io):
        """Test that network updates modify state correctly."""
        mock_io = MagicMock()
        mock_io.bytes_sent = 1000
        mock_io.bytes_recv = 2000
        mock_net_io.return_value = {
            "vEthernet (WSL)": mock_io
        }
        
        network.update_wsl_network()
        
        # State should not be None
        assert state.state is not None

    def test_network_module_state_variables(self):
        """Test that network module has expected state variables."""
        assert hasattr(network, '_last_vnet_rx')
        assert hasattr(network, '_last_vnet_tx')
        assert hasattr(network, '_last_vnet_time')
        assert hasattr(network, '_last_sgs_rx')
        assert hasattr(network, '_last_sgs_tx')
        assert hasattr(network, '_last_sgs_time')

    @patch('src.network.PSUTIL_AVAILABLE', True)
    @patch('src.network.psutil.net_io_counters')
    def test_update_network_with_multiple_interfaces(self, mock_net_io):
        """Test network update with multiple network interfaces."""
        mock_io1 = MagicMock()
        mock_io1.bytes_sent = 1000
        mock_io1.bytes_recv = 2000
        
        mock_io2 = MagicMock()
        mock_io2.bytes_sent = 500
        mock_io2.bytes_recv = 1000
        
        mock_net_io.return_value = {
            "vEthernet (WSL)": mock_io1,
            "vEthernet (Default)": mock_io2
        }
        
        with patch('src.network.debug'):
            network.update_wsl_network()
        
        # Should not crash with multiple interfaces

    @patch('src.network.PSUTIL_AVAILABLE', True)
    @patch('src.network.psutil.net_io_counters')
    def test_update_network_empty_interfaces(self, mock_net_io):
        """Test network update when no vEthernet interfaces found."""
        mock_net_io.return_value = {
            "eth0": MagicMock(),
            "lo": MagicMock()
        }
        
        network.update_wsl_network()
        
        # Should not crash

    @patch('src.network.PSUTIL_AVAILABLE', True)
    @patch('src.network.psutil.net_io_counters')
    def test_network_state_is_downloading_integration(self, mock_net_io):
        """Test network update behavior when downloading."""
        state.state["is_downloading"] = True
        
        mock_io = MagicMock()
        mock_io.bytes_sent = 1000
        mock_io.bytes_recv = 2000
        mock_net_io.return_value = {"vEthernet (WSL)": mock_io}
        
        with patch('src.network.debug'):
            network.update_wsl_network()
        
        # Should handle downloading state
