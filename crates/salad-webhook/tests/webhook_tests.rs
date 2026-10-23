use salad_webhook::db::{WebhookDatabase, WebhookRecord};
use salad_webhook::dispatcher::WebhookDispatcher;
use std::sync::Arc;
use tempfile::NamedTempFile;

#[test]
fn test_sqlite_schema_and_crud() {
    let tmp = NamedTempFile::new().unwrap();
    let db = WebhookDatabase::new(tmp.path()).unwrap();

    let rec = WebhookRecord {
        id: "hook-1".to_string(),
        url: "https://example.com/webhook".to_string(),
        secret: "supersecret".to_string(),
        event_types: vec!["job_started".to_string(), "job_stopped".to_string()],
        is_active: true,
        created_at: 123456789,
    };

    db.insert_webhook(&rec).unwrap();

    let list = db.list_webhooks().unwrap();
    assert_eq!(list.len(), 1);
    assert_eq!(list[0].id, "hook-1");
    assert_eq!(list[0].url, "https://example.com/webhook");

    db.delete_webhook("hook-1").unwrap();
    let list_after = db.list_webhooks().unwrap();
    assert_eq!(list_after.len(), 0);
}

#[test]
fn test_hmac_sha256_signature() {
    let secret = "secret_key";
    let payload = "{\"event\":\"job_started\"}";
    let sig = WebhookDispatcher::sign_payload(secret, payload);
    assert!(!sig.is_empty());
    assert_eq!(sig.len(), 64); // hex representation of 256 bits is 64 chars
}
