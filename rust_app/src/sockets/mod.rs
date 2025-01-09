
use futures::{StreamExt, SinkExt};
use tokio::sync::mpsc;
use warp::ws::{WebSocket, Message};
use crate::state::AppState;

pub mod listeners;

pub async fn handle_ws(ws: WebSocket, state: AppState) {
    let (mut ws_tx, mut ws_rx) = ws.split();

    // Create an mpsc channel for sending messages to this client
    let (tx, mut rx) = mpsc::channel::<Message>(100);

    // Spawn a task to forward messages from the mpsc receiver to the WebSocket sender
    tokio::spawn(async move {
        while let Some(message) = rx.recv().await {
            if let Err(e) = ws_tx.send(message).await {
                eprintln!("Error sending WebSocket message: {}", e);
                break;
            }
        }
    });

    // Handle incoming messages
    while let Some(Ok(msg)) = ws_rx.next().await {
        if msg.is_text() {
            let text = msg.to_str().unwrap();
            if let Ok(event) = serde_json::from_str::<listeners::Event>(text) {
                listeners::handle_event(event, tx.clone(), state.clone()).await;
            }
        }
    }
}
