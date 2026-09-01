//! Axum HTTP REST and SSE routes.

use crate::embed::static_handler;
use crate::state::{AppState, SseEvent, UnifiedSnapshot};
use axum::{
    extract::State,
    response::sse::{Event, Sse},
    routing::{get, post},
    Json, Router,
};
use futures::stream::Stream;
use std::convert::Infallible;
use std::sync::Arc;
use tokio_stream::wrappers::BroadcastStream;
use tokio_stream::StreamExt;

pub fn create_router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/api/v1/health", get(health_handler))
        .route("/api/v1/capabilities", get(capabilities_handler))
        .route("/api/v1/snapshot", get(snapshot_handler))
        .route("/api/v1/stream", get(sse_stream_handler))
        .fallback(static_handler)
        .with_state(state)
}

async fn health_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "ok",
        "version": "1.0.0",
        "timestamp": chrono::Utc::now().timestamp()
    }))
}

async fn capabilities_handler(State(state): State<Arc<AppState>>) -> Json<crate::state::Capabilities> {
    let snap = state.get_snapshot();
    Json(snap.capabilities)
}

async fn snapshot_handler(State(state): State<Arc<AppState>>) -> Json<UnifiedSnapshot> {
    Json(state.get_snapshot())
}

async fn sse_stream_handler(
    State(state): State<Arc<AppState>>,
) -> Sse<impl Stream<Item = Result<Event, Infallible>>> {
    let rx = state.broadcaster.subscribe();
    let stream = BroadcastStream::new(rx).filter_map(|msg| match msg {
        Ok(event) => match serde_json::to_string(&event) {
            Ok(json) => Some(Ok(Event::default().data(json))),
            Err(_) => None,
        },
        Err(_) => None,
    });

    Sse::new(stream)
}
