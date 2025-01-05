use warp::ws::Message;
use serde::Deserialize;
use warp::ws::WebSocket;
use warp::ws::WsSender;
use crate::state::AppState;

#[derive(Deserialize)]
pub struct Event {
    pub event: String,
    pub data: serde_json::Value,
}

pub async fn handle_event(event: Event, tx: &mut warp::ws::WsSender, state: AppState) {
    match event.event.as_str() {
        "connect" => connect(event.data, tx).await,
        "disconnect" => disconnect(event.data, tx).await,
        "enter_game_room" => enter_game_room(event.data, tx, state).await,
        _ => {
            let _ = tx.send(Message::text("Unknown event")).await;
        }
    }
}
async fn connect(data: serde_json::Value, tx: &mut warp::ws::WsSender) {
    // don't return anything, but print message to console
    println!("Client connected");
}

async fn disconnect(_data: serde_json::Value, tx: &mut WsSender) {
    // Send a close frame to the client
    if let Err(e) = tx.send(Message::close()).await {
        eprintln!("Failed to send close message: {}", e);
    }
    
    // Optionally give some time to process the close frame before dropping the sender
    sleep(Duration::from_millis(100)).await;

    println!("Client disconnected");
}

async fn enter_game_room(data: serde_json::Value, tx: &mut WsSender, state: AppState) {
    let game_id = data["gameId"].as_i32().unwrap();
    let user_id = data["userId"].unwrap();

    let game_durations = state.game_durations.lock().unwrap();
    if let Some(&duration) = game_durations.get(&game_id) {
        let mut game_rooms = state.game_rooms.lock().unwrap();
    
        // Insert the user into the game room with all relevant data
        game_rooms.insert(
            user_id,
            {
                let mut room_data = HashMap::new();
                room_data.insert("game_id".to_string(), GameRoomValue::Int(game_id)); // game_id as i32
                room_data.insert("duration".to_string(), GameRoomValue::Float(duration)); // duration as f64
                room_data.insert("client".to_string(), GameRoomValue::Sender(tx.clone())); // WebSocket sender
                room_data
            },
        );
        println!("User {} entered game room {}", user_id, game_id);
        // Notify the client that they entered the game room successfully
        let response = json!({
            "success": true,
            "message": "Entered game room"
        });
        let _ = tx.send(Message::text(response.to_string())).await;
    } else {
        // If the game ID does not exist, send an error message
        println("Game: {}, does not exist", game_id);
        let response = json!({
            "success": false,
            "message": "Game does not exist"
        });
        let _ = tx.send(Message::text(response.to_string())).await;
    }

}
