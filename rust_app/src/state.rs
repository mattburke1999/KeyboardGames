use std::collections::HashMap;
use std::sync::{Arc, Mutex};

#[derive(Clone, Debug)]
pub enum MetadataValue {
    Text(String),
    Flag(bool),
}

#[derive(Clone)]
pub struct AppState {
    pub game_rooms: Arc<Mutex<HashMap<String, HashMap<String, String>>>>, // Shared game rooms
    pub game_metadata: Arc<Mutex<HashMap<String, HashMap<String, MetadataValue>>>>, // Cached game metadata
}

impl AppState {
    pub fn new() -> Self {
        Self {
            game_rooms: Arc::new(Mutex::new(HashMap::new())),
            game_metadata: Arc::new(Mutex::new(HashMap::new())),
        }
    }
}
