use warp::{Filter, Rejection, Reply};
use crate::state::AppState;
use std::convert::Infallible;

pub fn endpoints(
    state: AppState,
) -> impl Filter<Extract = impl Reply, Error = Rejection> + Clone {
    let score_update = warp::path!("game" / u32 / "score_update")
        .and(warp::post())
        .and(with_state(state.clone()))
        .and(warp::body::json())
        .and_then(handle_score_update);

    let refresh_games = warp::path("refresh_games")
        .and(warp::post())
        .and(with_state(state))
        .and_then(handle_refresh_games);

    score_update.or(refresh_games)
}

fn with_state(
    state: AppState,
) -> impl Filter<Extract = (AppState,), Error = Infallible> + Clone {
    warp::any().map(move || state.clone())
}

async fn handle_score_update(
    game_id: u32,
    state: AppState,
    body: serde_json::Value, // Adjust the type based on your expected payload
) -> Result<impl Reply, Rejection> {
    // Extract and process data from `body`
    // Example: updating a score in the database
    let score = body.get("score").and_then(|s| s.as_u64()).unwrap_or(0);
    println!("Received score update for game {}: {}", game_id, score);

    // Perform operations using `state` or `game_id`
    Ok(warp::reply::json(&serde_json::json!({ "status": "success" })))
}

async fn handle_refresh_games(
    state: AppState,
) -> Result<impl Reply, Rejection> {
    // Logic to refresh game data
    println!("Refreshing games...");
    
    Ok(warp::reply::json(&serde_json::json!({ "status": "games refreshed" })))
}
