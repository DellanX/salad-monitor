import { computed, MaybeRefOrGetter, ref, toValue } from 'vue';
import { MetricSample, UnifiedSnapshot } from '../types';
import { ChartData, ChartDataset } from 'chart.js';

/**
 * Utility function for generating chart datasets from GPU history data 
 * @param historyData - The history data array to process
 * @param snapshot - Current snapshot with GPU devices
 * @param valueAccessor - Function that extracts the numeric value from each sample
 * @param labelPrefix - Prefix for dataset labels
 * @returns Dataset configuration object
 */
export function useHistoryDataset(
  snapshot: MaybeRefOrGetter<UnifiedSnapshot>,
  valueAccessor: (sample: MetricSample, gpuIndex: number) => number,
  labelPrefix: string
) {
  const labels = computed(() => toValue(snapshot)?.history?.map(sample => 
    new Date((sample as any).timestamp_secs * 1000).toLocaleTimeString()
  )) ?? [];

  const datasets = computed(() => toValue(snapshot).gpu?.devices.map((_, index) => {
    // Use a more eye-friendly hue shift (instead of 60 degrees, use 30 degrees)
    const hue = (index * 30) % 360;
    return {
      label: `${labelPrefix} ${index}`,
      data: toValue(snapshot)?.history?.map(sample => valueAccessor(sample, index)) ?? [],
      borderColor: `hsl(${hue}, 70%, 50%)`,
      backgroundColor: `hsla(${hue}, 70%, 50%, 0.2)`,
      tension: 0.4,
      fill: true
    } satisfies ChartDataset<"line", number[]>;
  }) ?? []);
  
  return {
    labels,
    datasets,
    chartData: computed<ChartData<'line', number[], string>>(() => ({ labels: labels.value, datasets: datasets.value }))
  };
}

/**
 * Utility function for generating a merged chart dataset from multiple value accessors
 * @param snapshot - Current snapshot with history data
 * @param valueAccessors - Array of functions that extract numeric values from each sample
 * @param labels - Array of labels for each dataset
 * @returns Merged dataset configuration object
 */
export function useMergedHistoryDataset(
  snapshot: MaybeRefOrGetter<UnifiedSnapshot>,
  valueAccessors: ((sample: MetricSample, gpuIndex: number) => number)[],
  labels: string[]
) {
  const mergedLabels = computed(() => toValue(snapshot)?.history?.map(sample => 
    new Date((sample as any).timestamp_secs * 1000).toLocaleTimeString()
  ) ?? []);

  const mergedDatasets = computed(() => {
    return valueAccessors.map((accessor, index) => {
      // Use a more eye-friendly hue shift for merged datasets
      const hue = (index * 30) % 360;
      const dataset: ChartDataset<"line", number[]> = {
        label: labels[index],
        data: toValue(snapshot)?.history?.map((sample, _) => {
          // For non-GPU data, we can't access GPU devices so we just use the accessor directly
          // This assumes the accessor works with single values or uses a different mechanism
          return accessor(sample, 0);
        }) ?? [],
        borderColor: `hsl(${hue}, 70%, 50%)`,
        backgroundColor: `hsla(${hue}, 70%, 50%, 0.2)`,
        tension: 0.4,
        fill: true
      };
      
      return dataset;
    });
  });

  return {
    labels: mergedLabels,
    datasets: mergedDatasets,
    chartData: computed<ChartData<'line', number[], string>>(() => ({ 
      labels: mergedLabels.value, 
      datasets: mergedDatasets.value 
    }))
  };
}