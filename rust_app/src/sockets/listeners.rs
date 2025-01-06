use warp::ws::Message;
use serde::Deserialize;
use warp::ws::WebSocket;
use warp::ws::WsSender;
use crate::state::AppState;
use uuid::Uuid;

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
        "start_game" => start_game(event.data, tx, state).await,
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
    } else {
        // If the game ID does not exist, send an error message
        println("Game: {}, does not exist", game_id);
        let response = json!({
            "success": false,
            "message": "Game does not exist"
        });
    }
    let _ = tx.send(Message::text(response.to_string())).await;
}

async fn timer(user_id: String, game_id: i32, tx: WsSender, duration: f64, end_game_token: String) {
    // TODO: Implement the timer logic
}

async fn start_game(data: serde_json::Value, tx: &mut WsSender, state: AppState) {
    let game_id = data["gameId"].as_i32().unwrap();
    let user_id = data["userId"].unwrap();

    let mut game_rooms = state.game_rooms.lock().unwrap();
    if let Some(room_data) = game_rooms.get_mut(&user_id) {
        if let Some(&GameRoomValue::Int(room_game_id)) = room_data.get("game_id") {
            if room_game_id == game_id {
                let start_game_token = Uuid::new_v4().to_string();
                let end_game_token = Uuid::new_v4().to_string();
                let response = json!({
                    "success": true,
                    "message": "Game started",
                    "start_game_token": start_game_token
                });
            } else {
                let response = json!({
                    "success": false,
                    "message": "Incorrect game room for user {}", user_id
                });
            }
        } else {
            let response = json!({
                "success": false,
                "message": "User {} is not in a game room", user_id
            });
        }
    } else {
        let response = json!({
            "success": false,
            "message": "User {} is not in a game room", user_id
        });
    }
    let _ = tx.send(Message::text(response.to_string())).await;
}
