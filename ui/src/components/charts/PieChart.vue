<template>
  <div class="w-full h-full">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PieController
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PieController
);

const props = defineProps<{
  chartData: {
    labels: string[];
    datasets: {
      data: number[];
      backgroundColor: string[];
    }[];
  };
  chartOptions?: any;
}>();

const chartCanvas = ref<HTMLCanvasElement | null>(null);
let chartInstance: ChartJS | null = null;

const createChart = () => {
  if (!chartCanvas.value) return;

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new ChartJS(chartCanvas.value, {
    type: 'pie',
    data: props.chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      ...props.chartOptions
    }
  });
};

onMounted(() => {
  createChart();
});

watch(
  () => [props.chartData, props.chartOptions],
  () => {
    createChart();
  },
  { deep: true }
);

defineExpose({
  chartInstance
});
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>