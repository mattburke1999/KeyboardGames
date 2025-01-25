use std::collections::HashMap;
use std::sync::Arc;
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
pub enum PoolValue {
    Pool(sqlx::PgPool),
    String(String)
}


#[derive(Clone)]
pub struct AppState {
    pub game_rooms: Arc<Mutex<HashMap<String, GameRoomData>>>, // Shared game rooms
    pub game_durations: Arc<Mutex<HashMap<i32, f64>>>, // Cached game metadata
    pub pg_pool: Arc<Mutex<PoolValue>>, // Shared database pool
}


impl AppState {
    pub fn new() -> Self {
        Self {
            game_rooms: Arc::new(Mutex::new(HashMap::new())),
            game_durations: Arc::new(Mutex::new(HashMap::new())),
            pg_pool: Arc::new(Mutex::new(PoolValue::String("".to_string()))),
        }
    }
}
