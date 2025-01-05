pub async fn handle_ws(ws: WebSocket, state: AppState) {
    let (mut tx, mut rx) = ws.split();

    while let Some(Ok(msg)) = rx.next().await {
        if msg.is_text() {
            let text = msg.to_str().unwrap();
            if let Ok(event) = serde_json::from_str::<listeners::Event>(text) {
                listeners::handle_event(event, &mut tx, state.clone()).await;
            }
        }
    }
}
