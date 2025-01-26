use std::collections::HashMap;
use std::sync::Arc;
use redis::Client;
use tokio::sync::Mutex;


#[derive(Clone, Debug, serde::Serialize)]
pub struct GameRoomData {
    pub game_id: Option<i32>,
    pub duration: Option<f64>,
    pub game_running: Option<bool>,
    pub point_list: Vec<serde_json::Value>,
    pub start_game_token: String,
    pub end_game_token: String
}


#[derive(Clone)]
pub struct AppState {
    pub game_rooms: Arc<Mutex<HashMap<String, GameRoomData>>>, // Shared game rooms
    pub game_durations: Arc<Mutex<HashMap<i32, f64>>>, // Cached game metadata
    pub sender_session_map: Arc<Mutex<HashMap<String, String>>>, // Shared mapper for senders
    pub pg_pool: Arc<sqlx::PgPool>, // Shared database pool
    pub redis_client: Arc<Client>, // Shared Redis client
}


impl AppState {
    pub fn new(redis_client: Arc<Client>, pg_pool:Arc<sqlx::PgPool>) -> Self {
        AppState {
            game_rooms: Arc::new(Mutex::new(HashMap::new())),
            game_durations: Arc::new(Mutex::new(HashMap::new())),
            sender_session_map: Arc::new(Mutex::new(HashMap::new())),
            pg_pool,
            redis_client,
        }
    }
}
