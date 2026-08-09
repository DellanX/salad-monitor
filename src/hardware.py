"""Hardware monitoring for CPU, RAM, GPU, and Disk metrics."""

import subprocess
import platform
import re
from typing import Optional, Dict, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("WARNING: psutil not available, hardware monitoring disabled")

from src.config import debug
from src import state as state_module


def update_cpu_metrics() -> None:
    """Update CPU name and load percentage."""
    if not PSUTIL_AVAILABLE:
        return
    
    try:
        # Get CPU load percentage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get CPU name
        cpu_name = _get_cpu_name()
        
        state_module.state["cpu_name"] = cpu_name
        state_module.state["cpu_load_pct"] = round(cpu_percent, 1)
        debug(f"CPU: {cpu_name} @ {cpu_percent}%")
    except Exception as e:
        debug(f"Error updating CPU metrics: {e}")


def update_ram_metrics() -> None:
    """Update RAM usage statistics."""
    if not PSUTIL_AVAILABLE:
        return
    
    try:
        mem = psutil.virtual_memory()
        
        used_gb = mem.used / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        load_pct = mem.percent
        
        state_module.state["ram_used_gb"] = round(used_gb, 2)
        state_module.state["ram_total_gb"] = round(total_gb, 2)
        state_module.state["ram_load_pct"] = round(load_pct, 1)
        debug(f"RAM: {used_gb:.1f}/{total_gb:.1f} GB ({load_pct}%)")
    except Exception as e:
        debug(f"Error updating RAM metrics: {e}")


def update_gpu_metrics() -> None:
    """Update GPU metrics using nvidia-smi."""
    try:
        # Try to run nvidia-smi
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,power.draw,temperature.gpu", 
             "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                parts = [p.strip() for p in output.split(',')]
                if len(parts) >= 4:
                    gpu_name = parts[0].replace("NVIDIA GeForce ", "").replace("NVIDIA ", "")
                    gpu_util = float(parts[1])
                    gpu_power = float(parts[2])
                    gpu_temp = float(parts[3])
                    
                    state_module.state["gpu_name"] = gpu_name
                    state_module.state["gpu_utilization_pct"] = round(gpu_util, 1)
                    state_module.state["gpu_power_watts"] = round(gpu_power, 1)
                    state_module.state["gpu_temperature_c"] = round(gpu_temp, 1)
                    debug(f"GPU: {gpu_name} @ {gpu_util}% | {gpu_power}W | {gpu_temp}°C")
                    return
        
        # Fallback: try to get GPU name at least
        gpu_name = _get_gpu_name_fallback()
        if gpu_name:
            state_module.state["gpu_name"] = gpu_name
            debug(f"GPU: {gpu_name} (SMI not available)")
    
    except Exception as e:
        debug(f"Error updating GPU metrics: {e}")


def update_disk_metrics() -> None:
    """Update disk type, usage, and I/O statistics."""
    if not PSUTIL_AVAILABLE:
        return
    
    try:
        # Get disk usage for the main partition
        disk_usage = psutil.disk_usage('/')
        
        used_gb = disk_usage.used / (1024 ** 3)
        total_gb = disk_usage.total / (1024 ** 3)
        util_pct = disk_usage.percent
        
        state_module.state["disk_size_gb"] = round(total_gb, 1)
        state_module.state["disk_utilization_pct"] = round(util_pct, 1)
        
        # Get disk I/O statistics
        try:
            io_counters = psutil.disk_io_counters()
            if io_counters:
                # Note: These are cumulative, would need to track delta for real MB/s
                # For now, just store the type
                disk_type = _detect_disk_type()
                state_module.state["disk_type"] = disk_type
                debug(f"DISK: {disk_type} {total_gb:.0f}GB @ {util_pct}%")
        except Exception:
            pass
            
    except Exception as e:
        debug(f"Error updating disk metrics: {e}")


def update_wsl_status() -> None:
    """Update WSL status and RAM usage."""
    if not PSUTIL_AVAILABLE:
        return
    
    try:
        # Check for WSL-related processes
        wsl_ram_bytes = 0
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if proc_name in ['vmmemwsl', 'vmmem', 'wslhost']:
                    wsl_ram_bytes += proc.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        wsl_ram_mb = wsl_ram_bytes / (1024 ** 2)
        state_module.state["wsl_ram_mb"] = round(wsl_ram_mb, 1) if wsl_ram_mb > 0 else None
        
        # Try to get WSL status (Windows only)
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ["wsl.exe", "-l", "-v"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    output = result.stdout.replace("\x00", "")
                    match = re.search(r"salad-enterprise-linux\s+([A-Za-z]+)", output)
                    if match:
                        state = match.group(1)
                        wsl_status = "Running" if "Running" in state else "Stopped" if "Stopped" in state else state
                        state_module.state["wsl_status"] = wsl_status
                        debug(f"WSL: {wsl_status} ({wsl_ram_mb:.0f} MB)")
                        return
            except Exception:
                pass
        
        # Default status based on RAM usage
        if wsl_ram_mb > 0:
            state_module.state["wsl_status"] = "Running"
        else:
            state_module.state["wsl_status"] = "Stopped"
            
    except Exception as e:
        debug(f"Error updating WSL status: {e}")


def _get_cpu_name() -> str:
    """Get CPU name/model."""
    try:
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
            winreg.CloseKey(key)
            return cpu_name.strip()
        elif platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
    except Exception:
        pass
    
    return "CPU"


def _get_gpu_name_fallback() -> Optional[str]:
    """Fallback method to get GPU name without nvidia-smi."""
    try:
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000")
            gpu_name = winreg.QueryValueEx(key, "DriverDesc")[0]
            winreg.CloseKey(key)
            return gpu_name
    except Exception:
        pass
    
    return None


def _detect_disk_type() -> str:
    """Detect disk type (SSD, HDD, NVMe)."""
    # This is a simplified detection - real detection would require platform-specific calls
    # For now, assume SSD if we can't determine
    return "SSD"


def update_all_hardware() -> None:
    """Update all hardware metrics."""
    update_cpu_metrics()
    update_ram_metrics()
    update_gpu_metrics()
    update_disk_metrics()
    update_wsl_status()
