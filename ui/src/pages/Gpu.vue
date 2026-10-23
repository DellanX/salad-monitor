<template>
  <div>
    <h1 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">GPU Monitoring</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">GPU Summary</h2>
        <div class="space-y-3">
          <div v-for="gpu in snapshot.gpu?.devices" :key="gpu.index" class="flex justify-between items-center">
            <span class="text-gray-900 dark:text-white">{{ gpu.name }}</span>
            <span class="font-mono text-gray-900 dark:text-white">{{ Math.round(gpu.gpu_utilization_pct) }}%</span>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Memory Usage</h2>
        <div class="space-y-3">
          <div v-for="gpu in snapshot.gpu?.devices" :key="gpu.index" class="flex justify-between items-center">
            <span class="text-gray-900 dark:text-white">{{ gpu.name }}</span>
            <span class="text-gray-900 dark:text-white">{{ Math.round(gpu.memory_utilization_pct) }}%</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div class="col-span-2 bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">GPU Usage History</h2>
        <div class="h-80">
          <LineChart v-if="gpuChartData" :chart-data="gpuChartData" :chart-options="gpuChartOptions" />
        </div>
      </div>
      
      <!-- GPU Power Usage History Chart -->
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">GPU Power Usage History</h2>
        <div class="h-80">
          <LineChart v-if="gpuPowerChartData" :chart-data="gpuPowerChartData" :chart-options="gpuPowerChartOptions" />
        </div>
      </div>
      
      <!-- GPU Temperature History Chart -->
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">GPU Temperature History</h2>
        <div class="h-80">
          <LineChart v-if="gpuTempChartData" :chart-data="gpuTempChartData" :chart-options="gpuTempChartOptions" />
        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">GPU Details</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">GPU</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Utilization</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Memory Used</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Temperature</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Power</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="gpu in snapshot.gpu?.devices" :key="gpu.index" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ gpu.name }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ Math.round(gpu.gpu_utilization_pct) }}%</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ formatBytes(gpu.memory_used_bytes) }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ gpu.temperature_c }}°C</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ gpu.power_usage_w }}W</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useTelemetryStore } from '../stores/telemetry';
import { formatBytes } from '../utils/formatters';
import LineChart from '../components/charts/LineChart.vue';
import { useHistoryDataset, useMergedHistoryDataset } from '../composables/chartUtils.ts';
import { ChartOptions } from 'chart.js';

const telemetry = useTelemetryStore();
const snapshot = computed(() => telemetry.snapshot);

const gpuChartOptions = {
  animation: false,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'GPU Usage History'
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
} satisfies ChartOptions;

const gpuPowerChartOptions = {
  animation: false,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'GPU Power Usage History'
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
        text: 'Power (W)'
      }
    }
  }
} satisfies ChartOptions;

const gpuTempChartOptions = {
  animation: false,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'GPU Temperature History'
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
        text: 'Temperature (°C)'
      }
    }
  }
} satisfies ChartOptions;

const { chartData: gpuChartData } = useMergedHistoryDataset(snapshot, [sample => sample.gpu_usage_pct ?? 0, sample => sample.gpu_memory_pct ?? 0], ["GPU Usage", "GPU Memory"]);
const { chartData: gpuPowerChartData } = useHistoryDataset(snapshot, sample => sample.power_w ?? 0, "GPU Power");
const { chartData: gpuTempChartData } = useHistoryDataset(snapshot, sample => sample.gpu_temp_c ?? 0, "GPU Temp");

</script>