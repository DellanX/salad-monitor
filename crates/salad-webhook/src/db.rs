//! SQLite database management via `rusqlite` for webhooks and delivery logs.

use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WebhookRecord {
    pub id: String,
    pub url: String,
    pub secret: String,
    pub event_types: Vec<String>,
    pub is_active: bool,
    pub created_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeliveryLogRecord {
    pub id: String,
    pub webhook_id: String,
    pub event_type: String,
    pub status_code: Option<u16>,
    pub attempt_count: u32,
    pub last_attempt_at: i64,
    pub error_message: Option<String>,
}

pub struct WebhookDatabase {
    conn_path: String,
}

impl WebhookDatabase {
    pub fn new<P: AsRef<Path>>(db_path: P) -> Result<Self> {
        let path_str = db_path.as_ref().to_string_lossy().to_string();
        let db = Self { conn_path: path_str };
        db.init_schema()?;
        Ok(db)
    }

    fn get_conn(&self) -> Result<Connection> {
        Connection::open(&self.conn_path)
    }

    pub fn init_schema(&self) -> Result<()> {
        let conn = self.get_conn()?;
        conn.execute(
            "CREATE TABLE IF NOT EXISTS webhooks (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                secret TEXT NOT NULL,
                event_types TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at INTEGER NOT NULL
            );",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS delivery_logs (
                id TEXT PRIMARY KEY,
                webhook_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                status_code INTEGER,
                attempt_count INTEGER NOT NULL,
                last_attempt_at INTEGER NOT NULL,
                error_message TEXT,
                FOREIGN KEY(webhook_id) REFERENCES webhooks(id) ON DELETE CASCADE
            );",
            [],
        )?;

        Ok(())
    }

    pub fn insert_webhook(&self, webhook: &WebhookRecord) -> Result<()> {
        let conn = self.get_conn()?;
        let events_json = serde_json::to_string(&webhook.event_types).unwrap_or_else(|_| "[]".to_string());
        conn.execute(
            "INSERT INTO webhooks (id, url, secret, event_types, is_active, created_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            params![
                webhook.id,
                webhook.url,
                webhook.secret,
                events_json,
                if webhook.is_active { 1 } else { 0 },
                webhook.created_at,
            ],
        )?;
        Ok(())
    }

    pub fn list_webhooks(&self) -> Result<Vec<WebhookRecord>> {
        let conn = self.get_conn()?;
        let mut stmt = conn.prepare("SELECT id, url, secret, event_types, is_active, created_at FROM webhooks")?;
        let rows = stmt.query_map([], |row| {
            let events_str: String = row.get(3)?;
            let event_types: Vec<String> = serde_json::from_str(&events_str).unwrap_or_default();
            let is_active: i32 = row.get(4)?;
            Ok(WebhookRecord {
                id: row.get(0)?,
                url: row.get(1)?,
                secret: row.get(2)?,
                event_types,
                is_active: is_active != 0,
                created_at: row.get(5)?,
            })
        })?;

        let mut list = Vec::new();
        for r in rows {
            list.push(r?);
        }
        Ok(list)
    }

    pub fn delete_webhook(&self, id: &str) -> Result<()> {
        let conn = self.get_conn()?;
        conn.execute("DELETE FROM webhooks WHERE id = ?1", params![id])?;
        Ok(())
    }

    pub fn log_delivery(&self, log: &DeliveryLogRecord) -> Result<()> {
        let conn = self.get_conn()?;
        conn.execute(
            "INSERT INTO delivery_logs (id, webhook_id, event_type, status_code, attempt_count, last_attempt_at, error_message)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            params![
                log.id,
                log.webhook_id,
                log.event_type,
                log.status_code,
                log.attempt_count,
                log.last_attempt_at,
                log.error_message,
            ],
        )?;
        Ok(())
    }
}

