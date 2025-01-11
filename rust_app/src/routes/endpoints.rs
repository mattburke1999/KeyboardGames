use warp::{Filter, Rejection, Reply, reject};
use std::convert::Infallible;
use serde_json::{json, Value};
use chrono::DateTime;

use crate::state::PoolValue;
use crate::state::AppState;
use crate::state::GameRoomValue;
use crate::db::update_score;
use crate::db::load_game_durations;
use crate::utils::convert_session_to_user_id;
use crate::utils::decode_session_token;
use crate::utils::InvalidPoolType;
use crate::utils::UtilError;



pub fn handle_endpoints(
    state: AppState,
) -> impl Filter<Extract = impl Reply, Error = Rejection> + Clone {
    let score_update = warp::path!("game" / u32 / "score_update")
        .and(warp::post())
        .and(with_state(state.clone()))
        .and(warp::body::json())
        .and_then(handle_score_update)
        .recover(handle_rejection);

    let get_session_data = warp::path!("get_session_data")
    .and(warp::post())
        .and(with_state(state.clone()))
        .and(warp::header::optional::<String>("Authorization"))
        .and_then(handle_get_session_data);

    let refresh_games = warp::path("refresh_games")
        .and(warp::post())
        .and(with_state(state))
        .and_then(handle_refresh_games);

    score_update.or(get_session_data).or(refresh_games)
}

fn with_state(
    state: AppState,
) -> impl Filter<Extract = (AppState,), Error = Infallible> + Clone {
    warp::any().map(move || state.clone())
}
async fn validate_points(
    server_point_list: Vec<Value>,
    client_point_list: &Vec<Value>,
    score: u32,
) -> (bool, serde_json::Value) {
    // println!("Server point list");
    // println!("{:?}", server_point_list);
    // println!("Client point list");
    // println!("{:?}", client_point_list);
    // println!("Score: {}", score);
    let latency_tolerance = 500; // 1 second for now will adjust later
    let invalid_point_response = (false, json!({"error": "Invalid point time"}));
    // check if len of server list is less than len of client list
    if server_point_list.len() < client_point_list.len() || score > server_point_list.len() as u32 || score > client_point_list.len() as u32 {
        return (false, json!({"error": "Too many points submitted"}));
    }
    //loop through client_point_list
    for i in 0..client_point_list.len() {
        let client_point = &client_point_list[i];
        if let (Some(client_token), Some(client_time)) = (
            client_point.get("point_token"),
            client_point.get("point_time"),
        ) {
            //find the corresponding server_point
            if let Some(server_point) = server_point_list.iter().find(|server_point| {
                server_point.get("point_token") == Some(client_token)
            }) {
                // check if point_time is within latency_tolerance
                // point times are strings in iso format
                let client_point_time = DateTime::parse_from_rfc3339(client_time.as_str().unwrap()).unwrap();
                let server_point_time = DateTime::parse_from_rfc3339(server_point.get("point_time").unwrap().as_str().unwrap()).unwrap();
                let actual_latency = server_point_time.signed_duration_since(client_point_time).num_milliseconds();
                if actual_latency.abs() > latency_tolerance {
                    println!("Server time: {}", server_point_time);
                    println!("Client time: {}", client_point_time);
                    return invalid_point_response;
                }
            } else {
                // No match found
                println!("No match found for client token: {}", client_token);
                return invalid_point_response;
            }
        } else {
            // Handle the case where "point_token" or "point_time" is missing
            eprintln!("Key 'point_token' or 'point_time' not found in client_point");
            return invalid_point_response;
        }
    }
    return (true, json!({"points": server_point_list.len()}));
}

// def validate_game(user_id, start_game_token, end_game_token, score, point_list):
async fn validate_game(
    state: AppState,
    session_id: String,
    start_game_token: &str,
    end_game_token: &str,
    score: u32,
    point_list: &Vec<Value>,
) -> (bool, serde_json::Value) {
    // compare start and end game tokens against server state
    // if tokens match, validate points
    // validate_points(server_point_list, point_list, score)
    let game_rooms = state.game_rooms.lock().await;
    let no_game_room_response = (false, json!({"error": "No game found for user"}));
    let room_data = game_rooms.iter().find(|(_, room_data)| {
        room_data.get("session_id").map(|v| {
            if let GameRoomValue::String(ref s) = v {
                s == &session_id
            } else {
                false
            }
        }).unwrap_or(false)
    });
    if let Some((_, room_data)) = room_data {
        // check if start and end token are in room_data
        if let Some(&GameRoomValue::String(ref start_game_token_server)) = room_data.get("start_game_token") {
            if let Some(&GameRoomValue::String(ref end_game_token_server)) = room_data.get("end_game_token") {
                if let Some(&GameRoomValue::List(ref point_list_server)) = room_data.get("point_list") {
                    if start_game_token_server == start_game_token && end_game_token_server == end_game_token{
                        // validate points
                        return validate_points(point_list_server.clone(), point_list, score).await;
                    } else {
                        return (false, json!({"error": "Invalid start or end game token"}));
                    }
                } else {
                    return no_game_room_response;
                }
            } else {
                return no_game_room_response;
            }
        } else {
            return no_game_room_response;
        }
    } else {
        return no_game_room_response;
    }
}



async fn handle_rejection(err: warp::Rejection) -> Result<impl warp::Reply, warp::Rejection> {
    if let Some(_) = err.find::<UtilError>() {
        Ok(warp::reply::with_status(
            "Invalid pool type".to_string(),
            warp::http::StatusCode::INTERNAL_SERVER_ERROR,
        ))
    } else {
        Err(err)
    }
}

async fn handle_score_update(
    game_id: u32,
    state: AppState,
    body: serde_json::Value, // Adjust the type based on your expected payload
) -> Result<impl Reply, Rejection> {
    let score = body["score"].as_u64().unwrap() as u32;
    let start_game_token = body["start_game_token"].as_str().unwrap();
    let end_game_token = body["end_game_token"].as_str().unwrap();
    let session_id = body["session_id"].as_str().unwrap();
    let user_id = convert_session_to_user_id(&session_id.to_string(), state.clone()).await;
    if user_id.is_err() {
        return Ok(warp::reply::json(&serde_json::json!({"error": "Invalid user"})));
    } else {
        let user_id = user_id.unwrap();
        let point_list = body["pointList"].as_array().unwrap();
        let game_validation_result = validate_game(state.clone(), session_id.to_string(), start_game_token, end_game_token, score, point_list).await;
        if !game_validation_result.0 {
            return Ok(warp::reply::json(&serde_json::json!(game_validation_result.1)));
        }
        println!("Score was validated");
        let score = game_validation_result.1["points"].as_u64().unwrap() as u32;
        // validate the game
        // if valid, insert the score into the database using pg function, which returns a list of top10 scores and top3 personal scores
        // respond with the list of top10 scores and top3 personal scores
        let high_scores;
        let points_added;
        let score_rank;
        let pg_pool = state.pg_pool.clone();
        let pool = pg_pool.lock().await;

        if let PoolValue::Pool(ref pg_pool) = *pool {
            (high_scores, points_added, score_rank) = update_score(pg_pool, user_id, score, game_id).await.unwrap();
        } else {
            // Handle the case where the PoolValue is not a PgPool
            return Err(reject::custom(InvalidPoolType));
        }
        let mut top10 = Vec::with_capacity(10);
        let mut top3 = Vec::with_capacity(3);
        for i in 0..high_scores.len() {
            let hs = high_scores[i].as_object().unwrap();
            let date = hs["score_date"].clone();
            let current_score = hs["current_score"].clone();
            let score = hs["score"].clone();
            if hs["score_type"] == "top10" {
                top10.push(json!({
                    "username": hs["username"],
                    "score": score,
                    "date": date,
                    "current_score": current_score
                }));
            } else if hs["score_type"] == "top3" {
                top3.push(json!({
                    "score": score,
                    "date": date,
                    "current_score": current_score
                }));
            }
        }
        Ok(warp::reply::json(&serde_json::json!({
            "top10": top10,
            "top3": top3,
            "points_added": points_added,
            "score_rank": score_rank
        })))
    }
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
    let mut response: serde_json::Value;
    let mut game_rooms = state.game_rooms.lock().await;
    if let Some(room_data) = game_rooms.remove(&session_id) {
        let start_game_token = room_data.get("start_game_token").unwrap();
        let end_game_token = room_data.get("end_game_token").unwrap();
        let point_list = room_data.get("point_list").unwrap();
        return Ok(warp::reply::json(&serde_json::json!({
                "start_game_token": start_game_token,
                "end_game_token": end_game_token,
                "point_list": point_list
            })));
    } else {
        return Ok(warp::reply::json(&serde_json::json!({
                "error": "No game data found for user"
            })));
    }
}
