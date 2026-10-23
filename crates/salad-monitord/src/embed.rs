//! Static file serving with embedded Vue 3 SPA via `rust-embed`.

use axum::{
    body::Body,
    http::{header, StatusCode, Uri},
    response::{IntoResponse, Response},
};
use rust_embed::RustEmbed;

#[derive(RustEmbed)]
#[folder = "../../ui/dist/"]
pub struct EmbeddedAssets;

pub async fn static_handler(uri: Uri) -> impl IntoResponse {
    let path = uri.path().trim_start_matches('/');

    let target_path = if path.is_empty() {
        "index.html"
    } else {
        path
    };

    match EmbeddedAssets::get(target_path) {
        Some(content) => {
            let mime = mime_guess::from_path(target_path).first_or_octet_stream();
            Response::builder()
                .status(StatusCode::OK)
                .header(header::CONTENT_TYPE, mime.as_ref())
                .body(Body::from(content.data))
                .unwrap()
        }
        None => {
            // SPA fallback to index.html for client-side routing
            if let Some(index_content) = EmbeddedAssets::get("index.html") {
                Response::builder()
                    .status(StatusCode::OK)
                    .header(header::CONTENT_TYPE, "text/html")
                    .body(Body::from(index_content.data))
                    .unwrap()
            } else {
                Response::builder()
                    .status(StatusCode::NOT_FOUND)
                    .body(Body::from("404 Not Found (Static UI assets missing)"))
                    .unwrap()
            }
        }
    }
}
