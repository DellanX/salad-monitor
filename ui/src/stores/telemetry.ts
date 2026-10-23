import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { useFetch } from '@vueuse/core'
import { UnifiedSnapshot } from '../types';

export const useTelemetryStore = defineStore('telemetry', () => {
  const disconnectedSnapshot: UnifiedSnapshot =  {
      capabilities: {
        disk_smart: false,
        gpu_nvidia: false,
        gpu_per_process: false,
        host_nic_vethernet: false,
        host_processes: false,
        log_parsing: false,
        miner_detection: false,
        salad_demand_api: false,
        windows_registry: false,
        wsl_status: false,
      },
      demand: [],
      history: [],
      log_state: {
        active_workloads_count: Number.NaN,
        download_speed_pct_per_sec: Number.NaN,
        global_progress: Number.NaN,
        layer_progress: [],
        recent_errors: [],
        recent_warnings: [],
        status: 'killed',
        wallet_balance: Number.NaN,
        wallet_projected: Number.NaN,
      },
      timestamp: Number.NaN,
      gpu: { devices: [], is_available: false }
    };
  const snapshotOrDefault = ref(disconnectedSnapshot);
  const { data: snapshot, execute: fetchSnapshot } = useFetch<UnifiedSnapshot>('/api/v1/snapshot', {
    immediate: true,
    initialData: disconnectedSnapshot,
    updateDataOnError: false,
    timeout: 5000,
  }).get().json<UnifiedSnapshot>();

  watch(snapshot, (v) => {
    if (v) {
      snapshotOrDefault.value = v;
    }
  })

  // Getters
  const uptime = computed(() => snapshotOrDefault.value.system?.system_info.uptime_secs ?? Number.NaN);
  const uptimeFormatted = computed(() => formatUptime(uptime.value ?? Number.NaN))

  let eventSource: EventSource | null = null;

  const connectSse = () => {
    // Establish SSE connection for real-time updates
    console.log('Connecting to SSE stream...')
    // Use the proxy path for SSE connection as well
    eventSource = new EventSource('/api/v1/stream')
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as { Snapshot: UnifiedSnapshot }
        snapshot.value = data.Snapshot || data
      } catch (error) {
        console.error('Error parsing SSE message:', error)
      }
    }
    
    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error)
      // Optionally reconnect on error
      // setTimeout(connectSse, 5000);
    }
  }

  const disconnectSse = () => {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
      console.log('Disconnected from SSE stream...')
    }
  }

  return {
    snapshot: snapshotOrDefault,
    uptime,
    uptimeFormatted,
    fetchSnapshot,
    connectSse,
    disconnectSse
  }
})

// Helper function for formatting uptime
function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else {
    return `${minutes}m`
  }
}