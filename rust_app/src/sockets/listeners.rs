use serde::Deserialize;
use warp::ws::Message;
use tokio::sync::mpsc;
use uuid::Uuid;
use serde_json::json;
use crate::state::AppState;
use tokio::time::Duration;
use std::collections::HashMap;
use futures::SinkExt;
use crate::state::GameRoomValue;

#[derive(Deserialize)]
pub struct Event {
    pub event: String,
    pub data: serde_json::Value,
}

pub async fn handle_event(event: Event, tx: &mpsc::Sender<Message>, state: AppState) {
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
async fn connect(_data: serde_json::Value, _tx: &mpsc::Sender<Message>) {
    // don't return anything, but print message to console
    println!("Client connected");
}

async fn disconnect(_data: serde_json::Value, tx: &mpsc::Sender<Message>) {
    // Send a close frame to the client
    if let Err(e) = tx.send(Message::close()).await {
        eprintln!("Failed to send close message: {}", e);
    }
    
    // Optionally give some time to process the close frame before dropping the sender
    tokio::time::sleep(Duration::from_millis(100)).await;

    println!("Client disconnected");
}

async fn enter_game_room(data: serde_json::Value, tx: &mpsc::Sender<Message>, state: AppState) {
    let game_id = data["gameId"].as_i64().unwrap() as i32;
    let user_id = data["userId"].as_i64().unwrap() as i32;

    let game_durations = state.game_durations.lock().await;
    let response;
    let response_event = "entered_game_room_response";
    if let Some(&duration) = game_durations.get(&game_id) {
        let mut game_rooms = state.game_rooms.lock().await;
    
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
        println!("User {} entered game room {}", user_id.to_string(), game_id.to_string());
        // Notify the client that they entered the game room successfully
        response = json!({
            "event": response_event,
            "success": true,
            "message": "Entered game room"
        });
    } else {
        // If the game ID does not exist, send an error message
        println!("Game: {}, does not exist", game_id.to_string());
        response = json!({
            "event": response_event,
            "success": false,
            "message": "Game does not exist"
        });
    }
    let _ = tx.send(Message::text(response.to_string())).await;
}

async fn game_timer(user_id: i32, game_id: i32, tx: mpsc::Sender<Message>, state: AppState, end_game_token: String) {
    // TODO: Implement the timer logic
    let duration;
    {
        let mut game_rooms = state.game_rooms.lock().await;
        // no need to check if room exists, as it was checked before spawning the task
        let room_data = game_rooms.get_mut(&user_id).unwrap(); 
        duration = match room_data.get("duration") {
            Some(GameRoomValue::Float(duration)) => duration.clone(),
            _ => 60.0 as f64,
        };
        room_data.insert("game_running".to_string(), GameRoomValue::Bool(true));
        room_data.insert("point_list".to_string(), GameRoomValue::List(Vec::new()));
    }
    tokio::time::sleep(Duration::from_secs_f64(duration)).await;
    {
        let mut game_rooms = state.game_rooms.lock().await;
        let room_data = game_rooms.get_mut(&user_id).unwrap();
        room_data.insert("game_running".to_string(), GameRoomValue::Bool(false));
    }
    emit_end_game(user_id, game_id, end_game_token, tx).await;
}

async fn emit_end_game(user_id: i32, game_id: i32, end_game_token: String, tx: mpsc::Sender<Message>) {
    println!("Ending game for user {} in game {}", user_id, game_id);
    let response = json!({
        "event": "end_game",
        "end_game_token": end_game_token
    });
    let _ = tx.send(Message::text(response.to_string())).await;
}


async fn start_game(data: serde_json::Value, tx: &mpsc::Sender<Message>, state: AppState) {
    let game_id = data["gameId"].as_i64().unwrap() as i32;
    let user_id = data["userId"].as_i64().unwrap() as i32;

    let response;
    let response_event = "start_game_response";
    let mut start_game_token = String::new();
    let mut end_game_token = String::new();
    {
        let mut game_rooms = state.game_rooms.lock().await;
        if let Some(room_data) = game_rooms.get_mut(&user_id) {
            if let Some(&GameRoomValue::Int(room_game_id)) = room_data.get("game_id") {
                if room_game_id == game_id {
                    start_game_token = Uuid::new_v4().to_string();
                    end_game_token = Uuid::new_v4().to_string();
                    room_data.insert("start_game_token".to_string(), GameRoomValue::String(start_game_token.clone()));
                    room_data.insert("end_game_token".to_string(), GameRoomValue::String(end_game_token.clone()));
                    response = json!({
                        "event": response_event,
                        "success": true,
                        "message": "Game started",
                        "start_game_token": start_game_token
                    });
                    
                } else {
                    response = json!({
                        "event": response_event,
                        "success": false,
                        "message": format!("Incorrect game room for user {}", user_id)
                    });
                }
            } else {
                response = json!({
                    "event": response_event,
                    "success": false,
                    "message": format!("User {} is not in a game room", user_id.to_string())
                });
            }
        } else {
            response = json!({
                "event": response_event,
                "success": false,
                "message": format!("User {} is not in a game room", user_id.to_string())
            });
        }
    }
    if response["success"].as_bool().unwrap_or(false) {
        tokio::spawn(game_timer(user_id, game_id, tx.clone(), state, end_game_token.clone())); // don't await
    }
    let _ = tx.send(Message::text(response.to_string())).await;
}
