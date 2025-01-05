use std::collections::HashMap;
use std::sync::{Arc, Mutex};

#[derive(Clone)]
pub struct AppState {
    pub game_rooms: Arc<Mutex<HashMap<String, HashMap<String, String>>>>, // Shared game rooms
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
