use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use warp::ws::WsSender;

// Define a custom enum for the values in the inner HashMap
#[derive(Clone, Debug)]
pub enum GameRoomValue {
    Bool(bool),
    String(String),
    List(Vec<String>),
    Sender(WsSender), // Add support for WebSocket senders
    Float(f64),
    Int(i32),
}

#[derive(Clone)]
pub struct AppState {
    pub game_rooms: Arc<Mutex<HashMap<i32, HashMap<String, GameRoomValue>>>>, // Shared game rooms
    pub game_durations: Arc<Mutex<HashMap<i32, f64>>>, // Cached game metadata
}

impl AppState {
    pub fn new() -> Self {
        Self {
            game_rooms: Arc::new(Mutex::new(HashMap::new())),
            game_durations: Arc::new(Mutex::new(HashMap::new())),
        }
    }
}
