<template>
  <div class="salad-monitor-app">
    <Header />
    <main class="dashboard-grid">
      <WorkloadPanel />
      <GpuPanel />
      <SystemPanel />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import Header from './components/Header.vue';
import WorkloadPanel from './components/WorkloadPanel.vue';
import GpuPanel from './components/GpuPanel.vue';
import SystemPanel from './components/SystemPanel.vue';
import { useTelemetryStore } from './stores/telemetry';

const telemetry = useTelemetryStore();

onMounted(() => {
  telemetry.fetchSnapshot();
  telemetry.connectSse();
});

onUnmounted(() => {
  telemetry.disconnectSse();
});
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
body {
  background: #0f172a;
  color: #f8fafc;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}
</style>

