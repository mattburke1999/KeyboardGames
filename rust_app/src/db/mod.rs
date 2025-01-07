pub mod actions;

// Optionally, re-export functions from the `actions` module for easier access
pub use actions::load_game_durations;

pub use actions::update_score;