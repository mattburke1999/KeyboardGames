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
async fn validate_points(
    server_point_list: Vec<u32>,
    client_point_list: Vec<u32>,
    score: u32,
) -> bool {
    // compare point tokens from server list vs client list
    // set some latency threshold and compare point_times from server list vs client list with latency
    // if tokens match and point_times are within latency, return true
}

// def validate_game(user_id, start_game_token, end_game_token, score, point_list):
async validate_game(
    user_id: u32,
    start_game_token: str,
    end_game_token: str,
    score: u32,
    point_list: Vec<u32>,
) -> bool {
    // compare start and end game tokens against server state
    // if tokens match, validate points
    // validate_points(server_point_list, point_list, score)
}

async fn handle_score_update(
    game_id: u32,
    state: AppState,
    body: serde_json::Value, // Adjust the type based on your expected payload
) -> Result<impl Reply, Rejection> {
    // validate the game
    // if valid, insert the score into the database using pg function, which returns a list of top10 scores and top3 personal scores
    // respond with the list of top10 scores and top3 personal scores

    // Perform operations using `state` or `game_id`
    Ok(warp::reply::json(&serde_json::json!({ "status": "success" })))
}

async fn refresh_games(
    state: AppState,
) {
    // Logic to refresh game data
    // refresh games
    println!("Refreshing games...");
}

async fn handle_refresh_games(
    state: AppState,
) -> Result<impl Reply, Rejection> {
    // this endpoint is called as part of the flask 'refresh_games' endpoint
    // the flask app and this rust app share a .env with a shared secret key
    // that key will be sent to this endpoint to verify the request
    // if the key is not present or incorrect, return an error
    // refresh game in background, respond immediately
    tokio::spawn(refresh_games(state.clone()));
    
    Ok(warp::reply::json(&serde_json::json!({ "status": "refreshing games" })))
}
