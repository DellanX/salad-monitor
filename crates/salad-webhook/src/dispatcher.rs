//! Async HTTP POST delivery dispatcher with HMAC signing and exponential backoff.

use crate::db::{DeliveryLogRecord, WebhookDatabase, WebhookRecord};
use hmac::{Hmac, Mac};
use reqwest::Client;
use sha2::Sha256;
use std::sync::Arc;
use std::time::Duration;

type HmacSha256 = Hmac<Sha256>;

pub struct WebhookDispatcher {
    client: Client,
    db: Arc<WebhookDatabase>,
}

impl WebhookDispatcher {
    pub fn new(db: Arc<WebhookDatabase>) -> Self {
        let client = Client::builder()
            .timeout(Duration::from_secs(10))
            .user_agent("salad-monitor-webhook/1.0")
            .build()
            .unwrap_or_default();

        Self { client, db }
    }

    /// Sign payload with HMAC-SHA256 secret.
    pub fn sign_payload(secret: &str, payload: &str) -> String {
        let mut mac = HmacSha256::new_from_slice(secret.as_bytes())
            .expect("HMAC can take key of any size");
        mac.update(payload.as_bytes());
        let result = mac.finalize();
        hex::encode(result.into_bytes())
    }

    /// Dispatch an event payload to a single registered webhook with exponential backoff.
    pub async fn dispatch(
        &self,
        webhook: &WebhookRecord,
        event_type: &str,
        payload_json: &str,
    ) -> Result<(), String> {
        if !webhook.is_active {
            return Ok(());
        }

        if !webhook.event_types.is_empty() && !webhook.event_types.iter().any(|e| e == event_type || e == "*") {
            return Ok(()); // Webhook not subscribed to this event type
        }

        let signature = Self::sign_payload(&webhook.secret, payload_json);
        let log_id = uuid::Uuid::new_v4().to_string();

        let mut attempts = 0;
        let max_attempts = 3;
        let mut backoff = Duration::from_millis(500);
        let mut last_status: Option<u16> = None;
        let mut last_error: Option<String> = None;

        while attempts < max_attempts {
            attempts += 1;
            let resp = self
                .client
                .post(&webhook.url)
                .header("Content-Type", "application/json")
                .header("X-Salad-Event", event_type)
                .header("X-Salad-Signature", format!("sha256={}", signature))
                .body(payload_json.to_string())
                .send()
                .await;

            match resp {
                Ok(response) => {
                    let status = response.status().as_u16();
                    last_status = Some(status);
                    if response.status().is_success() {
                        let _ = self.db.log_delivery(&DeliveryLogRecord {
                            id: log_id,
                            webhook_id: webhook.id.clone(),
                            event_type: event_type.to_string(),
                            status_code: Some(status),
                            attempt_count: attempts,
                            last_attempt_at: chrono::Utc::now().timestamp(),
                            error_message: None,
                        });
                        return Ok(());
                    } else {
                        last_error = Some(format!("HTTP error status {}", status));
                    }
                }
                Err(e) => {
                    last_error = Some(format!("Network error: {}", e));
                }
            }

            if attempts < max_attempts {
                tokio::time::sleep(backoff).await;
                backoff *= 2;
            }
        }

        let _ = self.db.log_delivery(&DeliveryLogRecord {
            id: log_id,
            webhook_id: webhook.id.clone(),
            event_type: event_type.to_string(),
            status_code: last_status,
            attempt_count: attempts,
            last_attempt_at: chrono::Utc::now().timestamp(),
            error_message: last_error.clone(),
        });

        Err(last_error.unwrap_or_else(|| "Delivery failed".to_string()))
    }
}

