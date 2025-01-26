use warp::{Filter, Rejection, Reply};
use std::convert::Infallible;

use crate::state::PoolValue;
use crate::state::AppState;
use crate::db::load_game_durations;



pub fn handle_endpoints(
    state: AppState,
) -> impl Filter<Extract = impl Reply, Error = Rejection> + Clone {

    let refresh_games = warp::path("refresh_games")
        .and(warp::post())
        .and(with_state(state))
        .and_then(handle_refresh_games);

    refresh_games
}

fn with_state(
    state: AppState,
) -> impl Filter<Extract = (AppState,), Error = Infallible> + Clone {
    warp::any().map(move || state.clone())
}

async fn refresh_games(
    state: AppState,
) {
    println!("Refreshing games...");
    let pg_pool = state.pg_pool.clone();
    let pool = pg_pool.lock().await;
    if let PoolValue::Pool(ref pg_pool) = *pool {
        load_game_durations(pg_pool, state.game_durations.clone()).await.unwrap();
        // Use high_scores, points_added, and score_rank here
    } else {
        // Handle the case where the PoolValue is not a PgPool
        return ;
    }
    
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
