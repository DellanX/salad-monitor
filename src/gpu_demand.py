"""GPU demand data fetcher from Salad API."""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("WARNING: requests not available, GPU demand API disabled")

from src.config import debug
from src import state as state_module


# Cache control
_last_fetch_time: Optional[datetime] = None
_cache_duration_minutes = 5
_is_fetching = False

GPU_DEMAND_API_URL = "https://app-api.salad.com/api/v2/demand-monitor/gpu"


async def fetch_gpu_demand_data() -> None:
    """Fetch GPU demand data from Salad API (async, cached for 5 minutes)."""
    global _last_fetch_time, _is_fetching
    
    if not REQUESTS_AVAILABLE:
        return
    
    # Skip if already fetching
    if _is_fetching:
        return
    
    # Skip if recently fetched (within cache duration)
    if _last_fetch_time:
        elapsed = datetime.now() - _last_fetch_time
        if elapsed < timedelta(minutes=_cache_duration_minutes):
            return
    
    _is_fetching = True
    
    try:
        # Get local GPU name
        local_gpu_name = state_module.state.get("gpu_name")
        
        if not local_gpu_name:
            debug("GPU demand: No local GPU name available yet")
            state_module.state["gpu_demand_tier"] = "Unknown GPU"
            _is_fetching = False
            return
        
        # Fetch data in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.get(
                GPU_DEMAND_API_URL,
                headers={"User-Agent": "Mozilla/5.0 SaladMonitor/2.0"},
                timeout=10
            )
        )
        
        if response.status_code != 200:
            debug(f"GPU demand API returned status {response.status_code}")
            state_module.state["gpu_demand_tier"] = "API Error"
            _is_fetching = False
            return
        
        gpus = response.json()
        
        # Find matching GPU
        my_gpu = None
        for gpu in gpus:
            gpu_name = gpu.get("name", "")
            gpu_display_name = gpu.get("displayName", "")
            
            if (gpu_name and gpu_name.lower() == local_gpu_name.lower()) or \
               (gpu_display_name and gpu_display_name.lower() == local_gpu_name.lower()):
                my_gpu = gpu
                break
        
        if my_gpu:
            # Extract demand data
            display_name = my_gpu.get("displayName", local_gpu_name)
            tier_name = my_gpu.get("demandTierName", "Unknown")
            utilization_pct = my_gpu.get("utilizationPct", 0)
            
            # Clamp utilization to 0-100
            if utilization_pct < 0:
                utilization_pct = 0
            if utilization_pct > 100:
                utilization_pct = 100
            
            earning_rates = my_gpu.get("earningRates", {})
            avg_rate = earning_rates.get("avgEarningRate", 0) * 24 if earning_rates else None
            max_rate = earning_rates.get("maxEarningRate", 0) * 24 if earning_rates else None
            
            recommended_specs = my_gpu.get("recommendedSpecs", {})
            recommended_ram_gb = recommended_specs.get("ramGb") if recommended_specs else None
            
            # Update state
            state_module.state["gpu_demand_tier"] = tier_name
            state_module.state["gpu_demand_utilization_pct"] = round(utilization_pct, 1)
            state_module.state["gpu_earning_avg_24h"] = round(avg_rate, 2) if avg_rate else None
            state_module.state["gpu_earning_max_24h"] = round(max_rate, 2) if max_rate else None
            state_module.state["gpu_recommended_ram_gb"] = recommended_ram_gb
            state_module.state["gpu_demand_last_update"] = datetime.now()
            
            debug(f"GPU_DEMAND: {display_name} - {tier_name} ({utilization_pct:.1f}% util) - Avg: ${avg_rate:.2f}/24h")
        else:
            # GPU not found in demand list
            state_module.state["gpu_demand_tier"] = f"Not Listed ({local_gpu_name})"
            state_module.state["gpu_demand_utilization_pct"] = None
            state_module.state["gpu_earning_avg_24h"] = None
            state_module.state["gpu_earning_max_24h"] = None
            state_module.state["gpu_recommended_ram_gb"] = None
            state_module.state["gpu_demand_last_update"] = datetime.now()
            debug(f"GPU_DEMAND: {local_gpu_name} not found in demand list")
        
        _last_fetch_time = datetime.now()
        
    except Exception as e:
        debug(f"Error fetching GPU demand data: {e}")
        state_module.state["gpu_demand_tier"] = "API Offline or Error"
    finally:
        _is_fetching = False


def fetch_gpu_demand_data_sync() -> None:
    """Synchronous wrapper for fetching GPU demand data."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create task
            asyncio.create_task(fetch_gpu_demand_data())
        else:
            # Otherwise run it directly
            loop.run_until_complete(fetch_gpu_demand_data())
    except Exception as e:
        debug(f"Error in sync GPU demand fetch: {e}")
