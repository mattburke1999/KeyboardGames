use serde::Deserialize;
use warp::ws::Message;
use tokio::sync::mpsc;
use uuid::Uuid;
use serde_json::json;
use tokio::time::Duration;

use crate::state::AppState;
use crate::state::GameRoomData;
use crate::utils::verify_session;
use crate::utils::decode_session_token;
use crate::db::rd_store_game_data;

#[derive(Deserialize)]
pub struct Event {
    pub event: String,
    pub data: serde_json::Value,
}
pub async fn handle_event(event: Event, tx: mpsc::Sender<Message>, client_ip_port: &str, state: AppState) {
    match event.event.as_str() {
        "connect" => connect(event.data, &tx).await,
        "disconnect" => disconnect(event.data, tx).await,
        "enter_game_room" => enter_game_room(event.data, tx, client_ip_port, state).await,
        "start_game" => start_game(event.data, tx, client_ip_port, state).await,
        "point_added" => point_added(event.data, tx, client_ip_port, state).await,
        _ => {
            let _ = tx.send(Message::text("Unknown event")).await;
        }
    }
}

async fn connect(_data: serde_json::Value, _tx: &mpsc::Sender<Message>) {
    // don't return anything, but print message to console
    println!("Client connected");
}
async fn disconnect(_data: serde_json::Value, tx: mpsc::Sender<Message>) {
    // Send a close frame to the client
    if let Err(e) = tx.send(Message::close()).await {
        eprintln!("Failed to send close message: {}", e);
    }
    
    // Optionally give some time to process the close frame before dropping the sender
    tokio::time::sleep(Duration::from_millis(100)).await;

    println!("Client disconnected");
}  



async fn enter_game_room(data: serde_json::Value, tx: mpsc::Sender<Message>, client_ip_port: &str, state: AppState) {
    let game_id = data["gameId"].as_i64().unwrap() as i32;
    let session_jwt = data["session_jwt"].as_str().unwrap();
    let response: serde_json::Value;
    let response_event = "entered_game_room_response";

    let decoded_token_result = decode_session_token(session_jwt);
    if !decoded_token_result.decoded {
        response = json!({
            "event": response_event,
            "success": false,
            "message": "Invalid session token"
        });
        let _ = tx.send(Message::text(response.to_string())).await;
        return;
    }

    let valid_session = verify_session(&decoded_token_result.session_id, &decoded_token_result.client_ip, &client_ip_port, &state).await;
    if let Err(err) = valid_session {
        print!("{:?}", err);
        response = json!({
            "event": response_event,
            "success": false,
            "message": "Invalid session"
        });
    } else {
        let game_durations = state.game_durations.lock().await;
        let response_event = "entered_game_room_response";
        if let Some(&duration) = game_durations.get(&game_id) {
            let mut game_rooms = state.game_rooms.lock().await;
            let mut sender_session_map = state.sender_session_map.lock().await;
            sender_session_map.insert(client_ip_port.to_string(), session_jwt.to_string());
            
            // Insert the user into the game room with all relevant data
            game_rooms.insert(
                session_jwt.to_string(), // session_jwt
                {
                    let room_data = GameRoomData {
                        game_id: Some(game_id),
                        duration: Some(duration),
                        game_running: Some(false),
                        point_list: Vec::new(),
                        start_game_token: String::new(),
                        end_game_token: String::new()
                    };
                    room_data
                },
            );
            println!("User entered game room {}", game_id.to_string());
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
    }
    let _ = tx.send(Message::text(response.to_string())).await;
}

async fn game_timer(game_id: i32, tx: mpsc::Sender<Message>, state: AppState, end_game_token: String, session_jwt: String) {
    // TODO: Implement the timer logic
    let duration;
    {
        let mut game_rooms = state.game_rooms.lock().await;
        let room_data = game_rooms.get_mut(&session_jwt).unwrap(); 
        duration = room_data.duration.unwrap();
        room_data.game_running = Some(true);
    }
    tokio::time::sleep(Duration::from_secs_f64(duration)).await;
    {
        let mut game_rooms = state.game_rooms.lock().await;
        let room_data = game_rooms.get_mut(&session_jwt).unwrap();
        room_data.game_running = Some(false);
    }
    emit_end_game(game_id, end_game_token, tx, &session_jwt, state).await;
}

async fn store_game_data(session_jwt: &str, tx: &mpsc::Sender<Message>, state: AppState) {
    let game_rooms = state.game_rooms.lock().await;
    if let Some(room_data) = game_rooms.get(&session_jwt.to_string()) {
        let data = serde_json::json!({
            "start_game_token": room_data.start_game_token,
            "end_game_token": room_data.end_game_token,
            "point_list": room_data.point_list
        });
        let redis_client = state.redis_client.clone();
        rd_store_game_data(redis_client, session_jwt, &data.to_string()).await.unwrap();
        let response = json!({
            "event": "game_data_stored",
            "success": true,
            "message": "Game data stored"
        });
        let _ = tx.send(Message::text(response.to_string())).await;
    }
}

async fn emit_end_game(game_id: i32, end_game_token: String, tx: mpsc::Sender<Message>, session_jwt: &str, state: AppState) {
    println!("Ending game for in game {}", game_id);
    let response = json!({
        "event": "end_game",
        "end_game_token": end_game_token
    });
    let session_jwt_clone = session_jwt.to_string();
    let tx_clone = tx.clone();
    tokio::spawn(async move {
        store_game_data(&session_jwt_clone, &tx_clone, state).await;
    });
    let _ = tx.send(Message::text(response.to_string())).await;
}

async fn verify_client_session(session_jwt: &str, client_ip_port: &str, state: AppState) -> bool {
    let sender_session_map = state.sender_session_map.lock().await;
    if let Some(stored_session_jwt) = sender_session_map.get(client_ip_port) {
        if stored_session_jwt == session_jwt {
            return true;
        }
    }
    return false;
}

async fn start_game(data: serde_json::Value, tx: mpsc::Sender<Message>, client_ip_port: &str, state: AppState) {
    let game_id = data["gameId"].as_i64().unwrap() as i32;
    let session_jwt = data["session_jwt"].as_str().unwrap();
    if !verify_client_session(session_jwt, client_ip_port, state.clone()).await{
        let _ = tx.send(Message::text(json!({
            "event": "start_game_response",
            "success": false,
            "message": "Invalid session"
        }).to_string())).await;
        return;
    }
    let response;
    let response_event = "start_game_response";
    let start_game_token = Uuid::new_v4().to_string();
    let end_game_token = Uuid::new_v4().to_string();
    {
        let mut game_rooms = state.game_rooms.lock().await;
        if let Some(room_data) = game_rooms.get_mut(&session_jwt.to_string()) {
            if room_data.game_id == Some(game_id) {
                room_data.start_game_token = start_game_token.clone();
                room_data.end_game_token = end_game_token.clone();
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
                    "message": format!("Incorrect game room for user")
                });
            }
        } else {
            response = json!({
                "event": response_event,
                "success": false,
                "message": format!("User is not in a game room")
            });
        }
        
    }
    if response["success"].as_bool().unwrap_or(false) {
        tokio::spawn(game_timer(game_id, tx.clone(), state, end_game_token.clone(), session_jwt.to_string())); // don't await
    }
    let _ = tx.send(Message::text(response.to_string())).await;
}

async fn point_added(data: serde_json::Value, tx: mpsc::Sender<Message> , client_ip_port: &str, state: AppState) {
    println!("Point added");
    println!("{:?}", data);
    let game_id = data["gameId"].as_i64().unwrap() as i32;
    let session_jwt = data["session_jwt"].as_str().unwrap();
    if !verify_client_session(session_jwt, client_ip_port, state.clone()).await{
        let _ = tx.send(Message::text(json!({
            "event": "start_game_response",
            "success": false,
            "message": "Invalid session"
        }).to_string())).await;
        return;
    }
    let response;
    let response_event = "point_added_response";
    let game_not_started_response = json!({
        "event": response_event,
        "success": false,
        "message": "Game not started"
    });
    let no_game_room_response = json!({
        "event": response_event,
        "success": false,
        "message": format!("User is not in a game room")
    });
    let mut game_rooms = state.game_rooms.lock().await;
    if let Some(room_data) = game_rooms.get_mut(&session_jwt.to_string()) {
        if room_data.game_id == Some(game_id) {
            if room_data.game_running.unwrap() {
                let point_token = Uuid::new_v4().to_string();
                // set point time to current time in iso8601 format that will match format of new Date().toISOString(),
                let point_time = chrono::Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
                room_data.point_list.push(json!({
                    "point_token": point_token,
                    "point_time": point_time
                }));
                response = json!({
                    "event": response_event,
                    "success": true,
                    "point_token": point_token,
                    "message": "Point added"
                });
            } else {
                response = game_not_started_response;
                println!("Game not started for user");
            }
        } else {
            response = json!({
                "event": response_event,
                "success": false,
                "message": format!("Incorrect game room for user")
            });
            println!("Incorrect game room for user");
        }
    } else {
        response = no_game_room_response;
        println!("User is not in a game room");
    }
    let _ = tx.send(Message::text(response.to_string())).await;
}