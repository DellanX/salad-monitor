//! Salad GPU Demand API client (`https://app-api.salad.com/api/v2/demand-monitor/gpu`).

use serde::{Deserialize, Serialize};
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuDemandInfo {
    pub id: String,
    pub name: String,
    pub demand_grade: String,
    pub price_usd_per_hr: f64,
}

pub struct DemandApiClient {
    client: reqwest::Client,
    cached_data: Option<Vec<GpuDemandInfo>>,
    last_fetch: Option<Instant>,
    cache_ttl: Duration,
}

impl DemandApiClient {
    pub fn new() -> Self {
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(10))
            .user_agent("salad-monitor/1.0")
            .build()
            .unwrap_or_default();

        Self {
            client,
            cached_data: None,
            last_fetch: None,
            cache_ttl: Duration::from_secs(300), // 5 minutes cache
        }
    }

    /// Fetches GPU demand information, utilizing the 5-minute cache.
    pub async fn fetch_demand(&mut self) -> Result<Vec<GpuDemandInfo>, String> {
        if let (Some(data), Some(last_fetch)) = (&self.cached_data, self.last_fetch) {
            if last_fetch.elapsed() < self.cache_ttl {
                return Ok(data.clone());
            }
        }

        let url = "https://app-api.salad.com/api/v2/demand-monitor/gpu";
        let resp = self
            .client
            .get(url)
            .send()
            .await
            .map_err(|e| format!("Demand API request failed: {}", e))?;

        if !resp.status().is_success() {
            return Err(format!("Demand API returned HTTP {}", resp.status()));
        }

        let gpus: Vec<GpuDemandInfo> = resp
            .json()
            .await
            .map_err(|e| format!("Failed to parse Demand API JSON response: {}", e))?;

        self.cached_data = Some(gpus.clone());
        self.last_fetch = Some(Instant::now());

        Ok(gpus)
    }

    /// Match an NVML GPU model string (e.g. "NVIDIA GeForce RTX 3080") against the demand API database.
    pub fn find_matching_demand<'a>(
        gpu_name: &str,
        demand_list: &'a [GpuDemandInfo],
    ) -> Option<&'a GpuDemandInfo> {
        let normalized = normalize_gpu_name(gpu_name);
        demand_list.iter().find(|item| {
            let item_norm = normalize_gpu_name(&item.name);
            !item_norm.is_empty() && (item_norm.contains(&normalized) || normalized.contains(&item_norm))
        })
    }
}

/// Normalizes GPU names for fuzzy matching.
pub fn normalize_gpu_name(name: &str) -> String {
    name.to_lowercase()
        .replace("nvidia", "")
        .replace("geforce", "")
        .replace("rtx", "")
        .replace("gtx", "")
        .replace("laptop gpu", "")
        .replace('-', " ")
        .split_whitespace()
        .collect::<Vec<&str>>()
        .join(" ")
}

