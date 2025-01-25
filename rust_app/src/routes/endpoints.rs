use warp::{Filter, Rejection, Reply};
use std::convert::Infallible;

use crate::state::PoolValue;
use crate::state::AppState;
use crate::db::load_game_durations;
use crate::utils::decode_session_token;



pub fn handle_endpoints(
    state: AppState,
) -> impl Filter<Extract = impl Reply, Error = Rejection> + Clone {

    let get_session_data = warp::path!("get_session_data")
    .and(warp::post())
        .and(with_state(state.clone()))
        .and(warp::header::optional::<String>("Authorization"))
        .and_then(handle_get_session_data);

    let refresh_games = warp::path("refresh_games")
        .and(warp::post())
        .and(with_state(state))
        .and_then(handle_refresh_games);

    get_session_data.or(refresh_games)
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


async fn handle_get_session_data(
    state: AppState,
    jwt: Option<String>,
) -> Result<impl Reply, Rejection> {
    // this endpoint is called internally by the flask server to get the session data
    // the flask server will generate a JWT token with session_id and current time stamp using shared secret key
    // the JWT and session_id will be sent to this endpoint
    // if the JWT is valid, return the session data
    let jwt_string = jwt.unwrap_or_else(|| "".to_string());

    if jwt_string.is_empty() {
        return Ok(warp::reply::json(&serde_json::json!({"error": "Missing Authorization header"})));
    }

    let token_response = decode_session_token(&jwt_string);
    if token_response.decoded == false {
        return Ok(warp::reply::json(&serde_json::json!({"error": "Invalid token"})));
    }
    let session_id = token_response.session_id;
    println!("Token is valid!");
    println!("Session ID: {:?}", session_id);
    let mut game_rooms = state.game_rooms.lock().await;
    if let Some(room_data) = game_rooms.remove(&jwt_string) {
        let response =serde_json::json!({
            "start_game_token": room_data.start_game_token,
            "end_game_token": room_data.end_game_token,
            "point_list": room_data.point_list
        });
        return Ok(warp::reply::json(&response));
    } else {
        return Ok(warp::reply::json(&serde_json::json!({
                "error": "No game data found for user"
            })));
    }
}
