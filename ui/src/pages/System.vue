<template>
  <div>
    <h1 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">System Information</h1>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Hardware Overview</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Hostname:</span>
            <span class="text-gray-900 dark:text-white">{{ snapshot.system?.system_info?.hostname }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">OS:</span>
            <span class="text-gray-900 dark:text-white">{{ snapshot.system?.system_info?.os_name }} {{ snapshot.system?.system_info?.os_version }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Architecture:</span>
            <span class="text-gray-900 dark:text-white">{{ snapshot.system?.system_info?.arch }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">CPU:</span>
            <span class="text-gray-900 dark:text-white">{{ snapshot.system?.cpu?.brand }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Memory:</span>
            <span class="text-gray-900 dark:text-white">{{ formatBytes(snapshot.system?.memory?.total_bytes ?? 0) }}</span>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">System Status</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Uptime:</span>
            <span class="text-gray-900 dark:text-white">{{ uptimeFormatted }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">CPU Load:</span>
            <span class="text-gray-900 dark:text-white">{{ Math.max((snapshot.system?.cpu?.usage_pct ?? 0, 1) * 100) }}%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Memory Usage:</span>
            <span class="text-gray-900 dark:text-white">{{ snapshot.system?.memory?.total_bytes ? Math.round((snapshot.system?.memory?.used_bytes ?? 0) / (snapshot.system?.memory?.total_bytes ?? 1) * 100) : 0 }}%</span>
          </div>
          <div class="mb-3">
            <div class="flex justify-between mb-1">
              <span class="text-gray-700 dark:text-gray-300">Memory Used:</span>
              <span class="text-gray-900 dark:text-white">{{ formatBytes(snapshot.system?.memory?.used_bytes ?? 0) }}</span>
            </div>
            <div class="flex justify-between mb-1">
              <span class="text-gray-700 dark:text-gray-300">Memory Total:</span>
              <span class="text-gray-900 dark:text-white">{{ formatBytes(snapshot.system?.memory?.total_bytes ?? 0) }}</span>
            </div>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-700 dark:text-gray-300">Network Adapters:</span>
            <span class="text-gray-900 dark:text-white">{{ snapshot.system?.networks?.length ?? 0 }}</span>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg lg:col-span-2 dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">CPU and Memory Usage History</h2>
        <div class="h-80">
          <LineChart v-if="cpuHistoryChartData" :chart-data="cpuHistoryChartData" :chart-options="chartOptions" />
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg lg:col-span-2 dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Network Adapters</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Interface</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">RX Rate</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">TX Rate</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Total RX</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Total TX</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="network in snapshot.system?.networks" :key="network.interface_name" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ network.interface_name }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ formatBytes(network.rx_rate_bytes_per_sec) }}/s</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ formatBytes(network.tx_rate_bytes_per_sec) }}/s</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ formatBytes(network.total_rx_bytes) }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ formatBytes(network.total_tx_bytes) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Storage</h2>
        <div class="space-y-3">
          <div v-for="disk in snapshot.system?.disks" :key="disk.name" class="mb-3">
            <div class="flex justify-between mb-1">
              <span class="text-gray-700 dark:text-gray-300">{{ disk.name }}</span>
              <span class="text-gray-900 dark:text-white">{{ Math.round(disk.usage_pct) }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
              <div 
                class="bg-blue-600 h-2.5 rounded-full" 
                :style="{ width: disk.usage_pct + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg lg:col-span-2 dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Network Usage History</h2>
        <div class="h-80">
          <LineChart v-if="networkChartData" :chart-data="networkChartData" :chart-options="networkChartOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useTelemetryStore } from '../stores/telemetry';
import { formatBytes, formatUptime } from '../utils/formatters';
import LineChart from '../components/charts/LineChart.vue';
import { useHistoryDataset, useMergedHistoryDataset } from '../composables/chartUtils.ts';

const telemetry = useTelemetryStore();
const snapshot = computed(() => telemetry.snapshot);
const uptimeFormatted = computed(() => formatUptime(snapshot.value.system?.system_info?.uptime_secs ?? 0));

// Prepare network chart data
const networkChartData = ref({
  labels: [] as string[],
  datasets: [
    {
      label: 'Network RX (bytes/s)',
      data: [] as number[],
      borderColor: '#f59e0b',
      backgroundColor: '#fbbf24',
      tension: 0.4,
      fill: true
    },
    {
      label: 'Network TX (bytes/s)',
      data: [] as number[],
      borderColor: '#8b5cf6',
      backgroundColor: '#a78bfa',
      tension: 0.4,
      fill: true
    }
  ]
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'CPU and Memory Usage History'
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Time'
      }
    },
    y: {
      title: {
        display: true,
        text: 'Usage (%)'
      },
      min: 0,
      max: 100
    }
  }
};

const networkChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'Network Usage History'
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Time'
      }
    },
    y: {
      title: {
        display: true,
        text: 'Bytes/s'
      },
      min: 0
    }
  }
};

const { chartData: cpuHistoryChartData } = useMergedHistoryDataset(snapshot, [sample => sample.cpu_usage_pct, sample => sample.memory_usage_pct], ["CPU Usage", "RAM Usage"]);
// const { chartData: netHistoryChartData } = useHistoryDataset(snapshot, sample => sample.cpu_usage_pct, "CPU Usage");
</script>