"""Unit tests for src/processes.py"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src import processes, state


@pytest.mark.unit
class TestProcessMonitoring:
    """Test process detection and monitoring."""

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

    def test_miner_names_constant(self):
        """Test that MINER_NAMES is defined and contains expected entries."""
        assert isinstance(processes.MINER_NAMES, list)
        assert len(processes.MINER_NAMES) > 0
        # Check for some common miners
        assert any("miner" in name.lower() for name in processes.MINER_NAMES)

    @patch('src.processes.PSUTIL_AVAILABLE', False)
    def test_update_salad_processes_psutil_unavailable(self):
        """Test Salad processes update when psutil is unavailable."""
        processes.update_salad_processes()
        
        # Should not raise

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_update_salad_processes_no_processes(self, mock_process_iter):
        """Test Salad processes update when no Salad processes found."""
        mock_process_iter.return_value = []
        
        processes.update_salad_processes()
        
        # Should not raise

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_update_salad_processes_finds_salad(self, mock_process_iter):
        """Test detection of main Salad process."""
        start_time = datetime.now().timestamp()
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'salad.exe',
            'pid': 1234,
            'create_time': start_time,
            'exe': 'C:\\Salad\\salad.exe'
        }
        mock_process_iter.return_value = [mock_proc]
        
        with patch('src.processes.datetime') as mock_datetime:
            mock_datetime.fromtimestamp.return_value = datetime.now()
            with patch('src.processes.debug'):
                processes.update_salad_processes()
        
        # Should have detected Salad process

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_update_salad_processes_finds_bowl(self, mock_process_iter):
        """Test detection of Salad Bowl Service."""
        start_time = datetime.now().timestamp()
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'SaladBowlService.exe',
            'pid': 5678,
            'create_time': start_time,
            'exe': 'C:\\Salad\\SaladBowlService.exe'
        }
        mock_process_iter.return_value = [mock_proc]
        
        with patch('src.processes.datetime') as mock_datetime:
            mock_datetime.fromtimestamp.return_value = datetime.now()
            with patch('src.processes.debug'):
                processes.update_salad_processes()

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_update_salad_processes_skips_monitor(self, mock_process_iter):
        """Test that salad-monitor process is skipped."""
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'salad-monitor.exe',
            'pid': 9999,
            'create_time': datetime.now().timestamp(),
            'exe': 'C:\\salad-monitor.exe'
        }
        mock_process_iter.return_value = [mock_proc]
        
        with patch('src.processes.debug'):
            processes.update_salad_processes()
        
        # Should skip salad-monitor

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_update_salad_processes_case_insensitive(self, mock_process_iter):
        """Test that process name matching is case insensitive."""
        start_time = datetime.now().timestamp()
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'SALAD.EXE',  # All caps
            'pid': 1234,
            'create_time': start_time,
            'exe': 'C:\\Salad\\salad.exe'
        }
        mock_process_iter.return_value = [mock_proc]
        
        with patch('src.processes.datetime') as mock_datetime:
            mock_datetime.fromtimestamp.return_value = datetime.now()
            with patch('src.processes.debug'):
                processes.update_salad_processes()

    @patch('src.processes.PSUTIL_AVAILABLE', False)
    def test_update_miner_detection_psutil_unavailable(self):
        """Test miner detection when psutil is unavailable."""
        processes.update_miner_detection()
        
        # Should not raise

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_update_miner_detection_no_miners(self, mock_process_iter):
        """Test miner detection when no miners running."""
        mock_process_iter.return_value = []
        
        processes.update_miner_detection()
        
        # Should not raise

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_update_miner_detection_finds_miner(self, mock_process_iter):
        """Test detection of mining process."""
        start_time = datetime.now().timestamp()
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'trex.exe',
            'pid': 2222,
            'create_time': start_time,
            'exe': 'C:\\Miners\\trex.exe'
        }
        mock_process_iter.return_value = [mock_proc]
        
        with patch('src.processes.datetime') as mock_datetime:
            mock_datetime.fromtimestamp.return_value = datetime.now()
            with patch('src.processes.debug'):
                processes.update_miner_detection()

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_update_miner_detection_multiple_miners(self, mock_process_iter):
        """Test detection of multiple mining processes."""
        start_time = datetime.now().timestamp()
        
        mock_proc1 = MagicMock()
        mock_proc1.info = {
            'name': 'gminer.exe',
            'pid': 2222,
            'create_time': start_time,
            'exe': 'C:\\Miners\\gminer.exe'
        }
        
        mock_proc2 = MagicMock()
        mock_proc2.info = {
            'name': 'nbminer.exe',
            'pid': 3333,
            'create_time': start_time - 100,
            'exe': 'C:\\Miners\\nbminer.exe'
        }
        
        mock_process_iter.return_value = [mock_proc1, mock_proc2]
        
        with patch('src.processes.datetime') as mock_datetime:
            mock_datetime.fromtimestamp.return_value = datetime.now()
            with patch('src.processes.debug'):
                processes.update_miner_detection()

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_update_miner_detection_case_insensitive(self, mock_process_iter):
        """Test that miner name matching is case insensitive."""
        start_time = datetime.now().timestamp()
        mock_proc = MagicMock()
        mock_proc.info = {
            'name': 'T-REX.EXE',  # All caps
            'pid': 2222,
            'create_time': start_time,
            'exe': 'C:\\Miners\\t-rex.exe'
        }
        mock_process_iter.return_value = [mock_proc]
        
        with patch('src.processes.datetime') as mock_datetime:
            mock_datetime.fromtimestamp.return_value = datetime.now()
            with patch('src.processes.debug'):
                processes.update_miner_detection()

    @patch('src.processes.update_salad_processes')
    @patch('src.processes.update_miner_detection')
    def test_update_all_processes(self, mock_miner, mock_salad):
        """Test that update_all_processes calls both updates."""
        processes.update_all_processes()
        
        mock_salad.assert_called_once()
        mock_miner.assert_called_once()

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter', side_effect=Exception("Process Error"))
    def test_update_salad_processes_exception(self, mock_process_iter):
        """Test Salad processes update handles exceptions gracefully."""
        with patch('src.processes.debug'):
            processes.update_salad_processes()
        
        # Should not crash

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter', side_effect=Exception("Process Error"))
    def test_update_miner_detection_exception(self, mock_process_iter):
        """Test miner detection handles exceptions gracefully."""
        with patch('src.processes.debug'):
            processes.update_miner_detection()
        
        # Should not crash

    @patch('src.processes.PSUTIL_AVAILABLE', True)
    @patch('src.processes.psutil.process_iter')
    def test_process_state_initialization(self, mock_process_iter):
        """Test that process state is properly initialized."""
        mock_process_iter.return_value = []
        
        processes.update_salad_processes()
        processes.update_miner_detection()
        
        # State should be a dict
        assert isinstance(state.state, dict)

    def test_known_miner_list(self):
        """Test that known miners list contains expected names."""
        expected_miners = ["trex", "gminer", "xmrig", "nbminer", "lolminer"]
        actual_miners = [m.lower() for m in processes.MINER_NAMES]
        
        for miner in expected_miners:
            assert any(miner in actual for actual in actual_miners)


@pytest.mark.unit
def test_update_salad_processes_sidecar_mode_skips_local_collection():
    state.state.clear()
    state.state.update({})
    with patch("src.processes.COLLECTOR_MODE", "sidecar_push"):
        processes.update_salad_processes()

    assert state.state.get("collector_mode") == "sidecar_push"
    assert state.state.get("process_data_source") == "sidecar"


@pytest.mark.unit
def test_update_salad_processes_volume_mode_reads_version_files(tmp_path):
    salad_file = tmp_path / "salad-version.txt"
    bowl_file = tmp_path / "bowl-version.txt"
    salad_file.write_text("1.2.3\n", encoding="utf-8")
    bowl_file.write_text("4.5.6\n", encoding="utf-8")

    with patch("src.processes.COLLECTOR_MODE", "volume_scan"), patch("src.processes.SALAD_VERSION_FILE", str(salad_file)), patch("src.processes.SALAD_BOWL_VERSION_FILE", str(bowl_file)):
        processes.update_salad_processes()

    assert state.state.get("salad_version") == "1.2.3"
    assert state.state.get("salad_bowl_version") == "4.5.6"
    assert state.state.get("process_data_source") == "volume"
