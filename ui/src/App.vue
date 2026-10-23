<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { useTelemetryStore } from './stores/telemetry';

const telemetry = useTelemetryStore();

onMounted(() => {
  telemetry.connectSse();
});

onUnmounted(() => {
  telemetry.disconnectSse();
});
</script>

