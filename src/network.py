"""Network monitoring for WSL and SGS processes."""

from datetime import datetime
from typing import Dict, List

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("WARNING: psutil not available, network monitoring disabled")

from src.config import debug
from src import state as state_module


# Network tracking state
_last_vnet_rx: int = 0
_last_vnet_tx: int = 0
_last_vnet_time: datetime = datetime.min

_last_sgs_rx: int = 0
_last_sgs_tx: int = 0
_last_sgs_time: datetime = datetime.min


def update_wsl_network() -> None:
    """Update WSL/VM network statistics (vEthernet interfaces)."""
    global _last_vnet_rx, _last_vnet_tx, _last_vnet_time
    
    if not PSUTIL_AVAILABLE:
        return
    
    try:
        current_rx = 0
        current_tx = 0
        
        # Find vEthernet interfaces
        net_io = psutil.net_io_counters(pernic=True)
        for interface_name, stats in net_io.items():
            if interface_name.startswith("vEthernet") or "WSL" in interface_name:
                # For WSL, host TX is VM RX and host RX is VM TX
                current_rx += stats.bytes_sent  # Host sends = VM receives
                current_tx += stats.bytes_recv  # Host receives = VM sends
        
        now = datetime.now()
        
        if _last_vnet_time != datetime.min:
            time_diff = (now - _last_vnet_time).total_seconds()
            
            if time_diff > 0:
                # Calculate speeds
                rx_diff = current_rx - _last_vnet_rx if current_rx > _last_vnet_rx else 0
                tx_diff = current_tx - _last_vnet_tx if current_tx > _last_vnet_tx else 0
                
                rx_kbps = (rx_diff / time_diff) / 1024.0
                tx_kbps = (tx_diff / time_diff) / 1024.0
                
                # Update download tracking if downloading
                if state_module.state.get("is_downloading", False):
                    download_mb_delta = rx_diff / (1024 ** 2)
                    current_total = state_module.state.get("download_total_mb", 0.0)
                    state_module.state["download_total_mb"] = current_total + download_mb_delta
                
                # Update totals
                total_rx_gb = current_rx / (1024 ** 3)
                total_tx_gb = current_tx / (1024 ** 3)
                
                state_module.state["vnet_rx_kbps"] = round(rx_kbps, 1)
                state_module.state["vnet_tx_kbps"] = round(tx_kbps, 1)
                state_module.state["vnet_total_rx_gb"] = round(total_rx_gb, 2)
                state_module.state["vnet_total_tx_gb"] = round(total_tx_gb, 2)
                
                debug(f"VNET: RX {rx_kbps:.1f} KB/s | TX {tx_kbps:.1f} KB/s")
        
        _last_vnet_rx = current_rx
        _last_vnet_tx = current_tx
        _last_vnet_time = now
        
    except Exception as e:
        debug(f"Error updating WSL network: {e}")


def update_sgs_network() -> None:
    """Update SGS/bandwidth process network statistics."""
    global _last_sgs_rx, _last_sgs_tx, _last_sgs_time
    
    if not PSUTIL_AVAILABLE:
        return
    
    try:
        # Find SGS-related processes
        sgs_process_names = ["sgs", "v2ray", "ss-local"]
        sgs_processes: List[psutil.Process] = []
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if any(sgs_name in proc_name for sgs_name in sgs_process_names):
                    sgs_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not sgs_processes:
            state_module.state["sgs_rx_kbps"] = None
            state_module.state["sgs_tx_kbps"] = None
            state_module.state["sgs_ram_mb"] = None
            _last_sgs_time = datetime.min
            return
        
        # Calculate total I/O and RAM
        current_rx = 0
        current_tx = 0
        total_ram_bytes = 0
        
        for proc in sgs_processes:
            try:
                io_counters = proc.io_counters()
                current_rx += io_counters.read_bytes
                current_tx += io_counters.write_bytes
                total_ram_bytes += proc.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        now = datetime.now()
        
        if _last_sgs_time != datetime.min:
            time_diff = (now - _last_sgs_time).total_seconds()
            
            if time_diff > 0:
                # Calculate speeds
                rx_diff = current_rx - _last_sgs_rx if current_rx > _last_sgs_rx else 0
                tx_diff = current_tx - _last_sgs_tx if current_tx > _last_sgs_tx else 0
                
                rx_kbps = (rx_diff / time_diff) / 1024.0
                tx_kbps = (tx_diff / time_diff) / 1024.0
                
                # Update totals
                total_rx_mb = state_module.state.get("sgs_total_rx_mb", 0.0) + (rx_diff / (1024 ** 2))
                total_tx_mb = state_module.state.get("sgs_total_tx_mb", 0.0) + (tx_diff / (1024 ** 2))
                ram_mb = total_ram_bytes / (1024 ** 2)
                
                state_module.state["sgs_rx_kbps"] = round(rx_kbps, 1)
                state_module.state["sgs_tx_kbps"] = round(tx_kbps, 1)
                state_module.state["sgs_total_rx_mb"] = round(total_rx_mb, 2)
                state_module.state["sgs_total_tx_mb"] = round(total_tx_mb, 2)
                state_module.state["sgs_ram_mb"] = round(ram_mb, 1)
                
                debug(f"SGS: RX {rx_kbps:.1f} KB/s | TX {tx_kbps:.1f} KB/s | RAM {ram_mb:.1f} MB")
        
        _last_sgs_rx = current_rx
        _last_sgs_tx = current_tx
        _last_sgs_time = now
        
    except Exception as e:
        debug(f"Error updating SGS network: {e}")


def update_all_network() -> None:
    """Update all network statistics."""
    update_wsl_network()
    update_sgs_network()
