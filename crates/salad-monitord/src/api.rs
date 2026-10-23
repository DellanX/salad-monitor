//! Axum HTTP REST and SSE routes.

use crate::embed::static_handler;
use crate::state::{AppState, UnifiedSnapshot};
use axum::{
    extract::State,
    response::sse::{Event, Sse},
    routing::get,
    Json, Router,
};
use futures::stream::Stream;
use std::convert::Infallible;
use std::sync::Arc;

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
    let stream = futures::stream::unfold(rx, |mut rx| async {
        match rx.recv().await {
            Ok(event) => {
                match serde_json::to_string(&event) {
                    Ok(json) => Some((Ok(Event::default().data(json)), rx)),
                    Err(_) => Some((Ok(Event::default().data("")), rx)), // Return empty event on serialization error
                }
            }
            Err(_) => None, // Channel closed
        }
    });

    Sse::new(stream)
}
