use warp::{Filter, Rejection, Reply};
use crate::state::AppState;
use std::convert::Infallible;
use crate::db::actions::update_score;

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
) -> (bool, serde_json::Value) {
    println!("Server point list");
    println!("{:?}", server_point_list);
    println!("Client point list");
    println!("{:?}", client_point_list);
    println!("Score: {}", score);
    let latency_tolerance = 1000; // 1 second for now will adjust later
    // check if len of server list is less than len of client list
    if server_point_list.len() < client_point_list.len() || score > server_point_list.len() as u32 || score > client_point_list.len() as u32 {
        return (false, json!({"error": "Too many points submitted"}));
    }
    //loop through client_point_list
    for i in 0..client_point_list.len() {
        let client_point = client_point_list[i] // {'point_token', 'point_time'}
        // find matching token in server_point_list
        if let Some(server_point) = server_point_list.iter().find(|&x| x.point_token == client_point.point_token) {
            if server_point.point_token != client_point.point_token {
                return (false, json!({"error": "Invalid point token"}));
            }
            // check if point_time is within latency_tolerance
            let actual_latency = server_point.point_time - client_point.point_time;
            if actual_latency.abs() > latency_tolerance {
                println!("Server time: {}", server_point.point_time);
                println!("Client time: {}", client_point.point_time);
                println!("Actual latency: {}", actual_latency);
                return (false, json!({"error": "Invalid point time"}));
            }
        } else {
            return (false, json!({"error": "Invalid point token"}));
        }
    }
    return (true, json!({"points": server_point_list.len()}));
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
) -> (bool, serde_json::Value) {
    // compare start and end game tokens against server state
    // if tokens match, validate points
    // validate_points(server_point_list, point_list, score)
    let mut game_rooms = state.game_rooms.lock().await;
    if let Some(room_data) = game_rooms.get_mut(&user_id) {
        // check if start and end token are in room_data
        if Some(start_game_token_server) == room_data.start_game_token && Some(end_game_token_server) == room_data.end_game_token {
            if start_game_token_server == start_game_token && end_game_token_server == end_game_token {
                // validate points
                return validate_points(room_data.point_list.clone(), point_list, score).await;
            } else {
                return (false, json!({"error": "Invalid start or end game token"}));
            }
        } else {
            return (false, json!({"error": "No game found for user"}));
        }
    } else {
        return (false, json!({"error": "No game found for user"}));
    }
}

async fn handle_score_update(
    game_id: u32,
    state: AppState,
    body: serde_json::Value, // Adjust the type based on your expected payload
) -> Result<impl Reply, Rejection> {
    // get data['score'], data['start_game_token'], data['end_game_token'], data['pointList'] from body
    let score = body["score"].as_u32().unwrap();
    let start_game_token = body["start_game_token"].as_str().unwrap();
    let end_game_token = body["end_game_token"].as_str().unwrap();
    let user_id = body["user_id"].as_u32().unwrap();
    let point_list = body["pointList"].as_array().unwrap();
    let game_validation_result = validate_game(user_id, start_game_token, end_game_token, score, point_list).await;
    if !game_validation_result.0 {
        return Ok(warp::reply::game_validation_result);
    }
    let score = game_validation_result.1["points"].as_u32().unwrap();
    // validate the game
    // if valid, insert the score into the database using pg function, which returns a list of top10 scores and top3 personal scores
    // respond with the list of top10 scores and top3 personal scores
    let pool = state.pool.clone();
    let (high_scores, points_added, score_rank) = update_score(&pool, user_id, score, game_id).await?;
    // top10 = [{
    //     **hs,
    //     'date': datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'),
    //     'current_score': hs['current_score']
    //     } for hs in high_scores if hs['score_type'] == 'top10']
    // top3 = [{
    //     'score': hs['score'],
    //     'date': datetime.strptime(hs['score_date'], '%Y-%m-%d').strftime('%m/%d/%Y'),
    //     'current_score': hs['current_score']
    //     } for hs in high_scores if hs['score_type'] == 'top3']
    let top10 = new Vec<serde_json::Value>();
    let top3 = new Vec<serde_json::Value>();
    for i in 0..high_scores.len() {
        let hs = high_scores[i];
        

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
