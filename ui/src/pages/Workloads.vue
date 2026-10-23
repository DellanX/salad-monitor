<template>
  <div>
    <h1 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Workload Management</h1>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Active Jobs</h2>
        <p class="text-3xl font-bold text-emerald-600 dark:text-emerald-400">{{ snapshot.workload_active_jobs }}</p>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Pending Tasks</h2>
        <p class="text-3xl font-bold text-amber-600 dark:text-amber-400">{{ snapshot.workload_pending_tasks }}</p>
      </div>
      
      <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
        <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Errors</h2>
        <p class="text-3xl font-bold text-red-600 dark:text-red-400">{{ snapshot.workload_errors }}</p>
      </div>
    </div>
    
    <div class="bg-white rounded-lg p-6 shadow-lg dark:bg-gray-800">
      <h2 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Active Workloads</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead>
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Job ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">GPU Type</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">Progress</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">ETA</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="job in snapshot.workload_jobs" :key="job.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ job.id }}</td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span :class="getJobStatusClass(job.status)">{{ job.status }}</span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ job.gpu_type }}</td>
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                  <div 
                    class="bg-emerald-500 h-2 rounded-full" 
                    :style="{ width: `${job.progress}%` }"
                  ></div>
                </div>
                {{ job.progress }}%
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-gray-900 dark:text-white">{{ formatDuration(job.eta_seconds) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useTelemetryStore } from '../stores/telemetry';
import { formatDuration } from '../utils/formatters';

const telemetry = useTelemetryStore();
const snapshot = computed(() => telemetry.snapshot);

const getJobStatusClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'running':
      return 'text-emerald-600 dark:text-emerald-400';
    case 'pending':
      return 'text-amber-600 dark:text-amber-400';
    case 'error':
      return 'text-red-600 dark:text-red-400';
    default:
      return 'text-gray-500 dark:text-gray-400';
  }
}
</script>