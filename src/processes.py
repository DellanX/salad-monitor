"""Process detection for Salad applications and miners."""

import platform
import subprocess
from datetime import datetime
from typing import Optional, List

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("WARNING: psutil not available, process detection disabled")

from src.config import debug
from src import state as state_module


# Known miner process names
MINER_NAMES = [
    "t-rex", "trex", "gminer", "srbminer", "xmrig", 
    "nbminer", "lolminer", "excavator", "rigel", 
    "bzminer", "phoenixminer", "miner"
]


def update_salad_processes() -> None:
    """Detect Salad and Salad Bowl Service processes, get versions and uptime."""
    if not PSUTIL_AVAILABLE:
        return
    
    try:
        salad_start_time: Optional[datetime] = None
        bowl_start_time: Optional[datetime] = None
        salad_version: Optional[str] = None
        bowl_version: Optional[str] = None
        salad_exe_path: Optional[str] = None
        bowl_exe_path: Optional[str] = None
        
        # Find Salad processes
        for proc in psutil.process_iter(['name', 'pid', 'create_time', 'exe']):
            try:
                proc_name = proc.info['name'].lower()
                
                # Skip our own process
                if "salad-monitor" in proc_name or "xray" in proc_name:
                    continue
                
                # Check for main Salad app
                if proc_name == "salad" or proc_name == "salad.exe" or "salad (amd edition)" in proc_name:
                    try:
                        start_time = datetime.fromtimestamp(proc.info['create_time'])
                        if not salad_start_time or start_time < salad_start_time:
                            salad_start_time = start_time
                        if proc.info.get('exe'):
                            salad_exe_path = proc.info['exe']
                    except Exception:
                        pass
                
                # Check for Salad Bowl Service
                elif "bowl" in proc_name or "salad.bowl.service" in proc_name:
                    try:
                        start_time = datetime.fromtimestamp(proc.info['create_time'])
                        if not bowl_start_time or start_time < bowl_start_time:
                            bowl_start_time = start_time
                        if proc.info.get('exe'):
                            bowl_exe_path = proc.info['exe']
                    except Exception:
                        pass
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Get versions from executables
        if salad_exe_path:
            salad_version = _get_version_from_file(salad_exe_path)
        
        if bowl_exe_path:
            bowl_version = _get_version_from_file(bowl_exe_path)
        elif platform.system() == "Windows":
            # Try registry fallback for Bowl Service
            bowl_exe_path = _get_bowl_service_path_from_registry()
            if bowl_exe_path:
                bowl_version = _get_version_from_file(bowl_exe_path)
        
        # Calculate uptimes
        salad_uptime = None
        if salad_start_time:
            salad_uptime = (datetime.now() - salad_start_time).total_seconds()
        
        bowl_uptime = None
        if bowl_start_time:
            bowl_uptime = (datetime.now() - bowl_start_time).total_seconds()
        
        # Update state
        state_module.state["salad_version"] = salad_version
        state_module.state["salad_uptime_seconds"] = salad_uptime
        state_module.state["salad_bowl_version"] = bowl_version if bowl_version else ("Offline" if not bowl_start_time else "Unknown")
        state_module.state["salad_bowl_uptime_seconds"] = bowl_uptime
        
        debug(f"SALAD: v{salad_version} (uptime: {salad_uptime}s), Bowl: v{bowl_version} (uptime: {bowl_uptime}s)")
        
    except Exception as e:
        debug(f"Error updating Salad processes: {e}")


def update_miner_detection() -> None:
    """Detect active miner processes."""
    if not PSUTIL_AVAILABLE:
        return
    
    try:
        miner_found = False
        miner_name = None
        
        for miner in MINER_NAMES:
            try:
                processes = [p for p in psutil.process_iter(['name']) 
                           if miner in p.info['name'].lower()]
                if processes:
                    miner_found = True
                    miner_name = processes[0].info['name']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        state_module.state["miner_active"] = miner_found
        state_module.state["miner_name"] = miner_name
        
        if miner_found:
            debug(f"MINER: Active - {miner_name}")
        
    except Exception as e:
        debug(f"Error detecting miner: {e}")


def _get_version_from_file(file_path: str) -> Optional[str]:
    """Extract version from executable file."""
    try:
        if platform.system() == "Windows":
            # Use PowerShell to get file version on Windows
            result = subprocess.run(
                ["powershell", "-Command", 
                 f"(Get-Item '{file_path}').VersionInfo.FileVersion"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                if version:
                    return version
        # For Linux, would need different approach (e.g., parse from --version flag)
    except Exception:
        pass
    
    return None


def _get_bowl_service_path_from_registry() -> Optional[str]:
    """Get Salad Bowl Service path from Windows registry."""
    if platform.system() != "Windows":
        return None
    
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SYSTEM\CurrentControlSet\Services\SaladBowl")
        image_path = winreg.QueryValueEx(key, "ImagePath")[0]
        winreg.CloseKey(key)
        
        if image_path:
            # Clean up the path
            image_path = image_path.replace('"', '').strip()
            if "--sb" in image_path:
                sb_index = image_path.index("--sb")
                image_path = image_path[sb_index + 4:].strip()
            
            if ".exe" in image_path.lower():
                exe_index = image_path.lower().index(".exe")
                image_path = image_path[:exe_index + 4]
            
            return image_path
    except Exception:
        pass
    
    # Fallback path
    fallback = r"C:\Program Files\Salad\SaladBowl\Salad.Bowl.Service.exe"
    try:
        import os
        if os.path.exists(fallback):
            return fallback
    except Exception:
        pass
    
    return None


def update_all_processes() -> None:
    """Update all process information."""
    update_salad_processes()
    update_miner_detection()
