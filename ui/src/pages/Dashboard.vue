<template>
  <div>
    <h1 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Dashboard Overview</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">System Status</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Uptime:</span>
            <span class="font-mono text-gray-900 dark:text-white">{{ uptimeFormatted }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">CPU Load:</span>
            <span class="text-gray-900 dark:text-white">{{ formatCpuLoad(snapshot.system?.cpu.usage_pct) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Memory:</span>
            <span class="text-gray-900 dark:text-white">{{ formatBytes(snapshot?.system?.memory.used_bytes ?? Number.NaN) }} / {{ formatBytes(snapshot?.system?.memory.total_bytes ?? Number.NaN) }}</span>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">GPU Status</h2>
        <div class="space-y-3">
          <div v-for="gpu in snapshot?.gpu?.devices ?? []" :key="gpu.index" class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">{{ gpu.name }}:</span>
            <span class="text-gray-900 dark:text-white">{{ Math.round(gpu.gpu_utilization_pct) }}%</span>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Workloads</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Active Workloads:</span>
            <span class="text-gray-900 dark:text-white">{{ snapshot?.log_state?.active_workloads_count ?? 0 }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Recent Errors:</span>
            <span class="text-red-500 dark:text-red-400">{{ snapshot?.log_state?.recent_errors.length ?? 0 }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Recent Warnings:</span>
            <span class="text-yellow-500 dark:text-yellow-400">{{ snapshot?.log_state?.recent_warnings.length ?? 0 }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Recent Activity</h2>
        <div class="space-y-3">
          <!-- <div v-for="activity in snapshot?.log_state?.activity ?? []" :key="activity.timestamp" class="flex items-start space-x-3">
            <div class="bg-emerald-500 rounded-full w-2 h-2 mt-2"></div>
            <div>
              <p class="text-sm text-gray-900 dark:text-white">{{ activity.message }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatTimestamp(activity.timestamp) }}</p>
            </div>
          </div> -->
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">System Metrics</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">CPU Usage:</span>
            <span class="text-gray-900 dark:text-white">{{ Math.round((snapshot?.system?.cpu.usage_pct ?? Number.NaN) * 100) }}%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Network Adapters:</span>
            <span class="text-gray-900 dark:text-white">{{ snapshot?.system?.networks?.length ?? 0 }}</span>
          </div>
          <div v-for="(network, index) in snapshot?.system?.networks" :key="index" class="ml-4">
            <div class="flex justify-between">
              <span class="text-gray-700 dark:text-gray-300">{{ network.interface_name }} In:</span>
              <span class="text-gray-900 dark:text-white">{{ formatBytes(network.rx_rate_bytes_per_sec ?? Number.NaN) }}/s</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-700 dark:text-gray-300">{{ network.interface_name }} Out:</span>
              <span class="text-gray-900 dark:text-white">{{ formatBytes(network.tx_rate_bytes_per_sec ?? Number.NaN) }}/s</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useTelemetryStore } from '../stores/telemetry';
import { formatBytes } from '../utils/formatters';

const { snapshot, uptimeFormatted } = storeToRefs(useTelemetryStore());

// Format CPU load to make it more intuitive
function formatCpuLoad(usagePct: number | undefined): string {
  if (usagePct === undefined || isNaN(usagePct)) {
    return 'N/A';
  }
  
  // Convert to percentage and show both total and per-core values
  const total = Math.round(usagePct * 100);
  return `${total}%`;
}
</script>