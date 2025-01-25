
use futures::{StreamExt, SinkExt};
use tokio::sync::mpsc;
use warp::ws::{WebSocket, Message};
use crate::state::AppState;
use std::net::SocketAddr;

pub mod listeners;

pub async fn handle_ws(ws: WebSocket, client_addr: Option<SocketAddr>, state: AppState) {
    // Log the client's IP and port
    let client_ip_port = client_addr.map(|addr| addr.to_string()).unwrap_or_else(|| "unknown".to_string());
    if client_ip_port != "unknown" {
        println!("Client connected from: {}", client_ip_port);
    } else {
        println!("Could not determine client address.");
    }

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
                listeners::handle_event(event, tx.clone(), &client_ip_port, state.clone()).await;
            }
        }
    }
}
