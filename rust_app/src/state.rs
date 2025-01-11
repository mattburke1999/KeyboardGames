use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{Mutex, mpsc};
use tokio::sync::mpsc::Sender;
use warp::ws::Message;
use serde_json::Value;

// Define a custom enum for the values in the inner HashMap
#[derive(Clone, Debug, serde::Serialize)]
pub enum GameRoomValue {
    Bool(bool),
    String(String),
    List(Vec<Value>),
    Float(f64),
    Int(i32),
}
pub enum PoolValue {
    Pool(sqlx::PgPool),
    String(String)
}


#[derive(Clone)]
pub struct AppState {
    pub game_rooms: Arc<Mutex<HashMap<String, HashMap<String, GameRoomValue>>>>, // Shared game rooms
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
