export interface Capabilities {
  log_parsing: boolean;
  salad_demand_api: boolean;
  gpu_nvidia: boolean;
  gpu_per_process: boolean;
  miner_detection: boolean;
  host_processes: boolean;
  wsl_status: boolean;
  windows_registry: boolean;
  host_nic_vethernet: boolean;
  disk_smart: boolean;
}

export interface CpuMetrics {
  usage_pct: number;
  core_count: number;
  brand: string;
}

export interface MemoryMetrics {
  total_bytes: number;
  used_bytes: number;
  free_bytes: number;
  usage_pct: number;
}

export interface DiskMetrics {
  name: string;
  mount_point: string;
  total_bytes: number;
  available_bytes: number;
  usage_pct: number;
  is_removable: boolean;
}

export interface NetworkMetrics {
  interface_name: string;
  total_rx_bytes: number;
  total_tx_bytes: number;
  rx_rate_bytes_per_sec: number;
  tx_rate_bytes_per_sec: number;
}

export interface SystemInfo {
  hostname: string;
  os_name: string;
  os_version: string;
  kernel_version: string;
  arch: string;
  uptime_secs: number;
}

export interface SystemTelemetrySnapshot {
  system_info: SystemInfo;
  cpu: CpuMetrics;
  memory: MemoryMetrics;
  disks: DiskMetrics[];
  networks: NetworkMetrics[];
}

export interface GpuProcessInfo {
  pid: number;
  used_memory_bytes?: number;
  process_type: 'compute' | 'graphics';
}

export interface GpuDeviceMetrics {
  uuid: string;
  index: number;
  name: string;
  gpu_utilization_pct: number;
  memory_utilization_pct: number;
  memory_total_bytes: number;
  memory_used_bytes: number;
  memory_free_bytes: number;
  temperature_c: number;
  power_usage_w: number;
  power_limit_w?: number;
  fan_speed_pct?: number;
  clock_sm_mhz?: number;
  clock_memory_mhz?: number;
  pcie_tx_kbps?: number;
  pcie_rx_kbps?: number;
  running_processes: GpuProcessInfo[];
}

export interface GpuTelemetrySnapshot {
  is_available: boolean;
  devices: GpuDeviceMetrics[];
}

export interface LayerProgressInfo {
  layer_sha: string;
  progress: number;
}

export interface LogStateSnapshot {
  status: 'idle' | 'downloading' | 'running' | 'killed' | 'failed';
  workload_id?: string;
  global_progress: number;
  layer_progress: LayerProgressInfo[];
  download_speed_pct_per_sec: number;
  eta_seconds?: number;
  wallet_balance: number;
  wallet_projected: number;
  bandwidth_node?: string;
  distro_size_gb?: number;
  active_workloads_count: number;
  recent_errors: string[];
  recent_warnings: string[];
  last_heartbeat?: string;
}

export interface GpuDemandInfo {
  id: string;
  name: string;
  demand_grade: string;
  price_usd_per_hr: number;
}

export interface MetricSample {
  timestamp_secs: number;
  cpu_usage_pct: number;
  memory_usage_pct: number;
  gpu_usage_pct?: number;
  gpu_temp_c?: number;
  power_w?: number;
}

export interface UnifiedSnapshot {
  timestamp: number;
  capabilities: Capabilities;
  system?: SystemTelemetrySnapshot;
  gpu?: GpuTelemetrySnapshot;
  log_state: LogStateSnapshot;
  demand: GpuDemandInfo[];
  history: MetricSample[];
}

export interface WebhookRecord {
  id: string;
  url: string;
  secret: string;
  event_types: string[];
  is_active: boolean;
  created_at: number;
}
