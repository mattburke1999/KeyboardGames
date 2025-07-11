use sqlx::PgPool;
use std::collections::HashMap;
use std::sync::Arc;
use redis::{AsyncCommands, Client};
use tokio::sync::Mutex;

pub async fn load_game_durations (
    pool: &PgPool,
    game_durations: Arc<Mutex<HashMap<i32, f64>>>,
) -> Result<(), sqlx::Error> {
    let rows = sqlx::query!("SELECT id, duration from games")
        .fetch_all(pool)
        .await?;
    
    let mut durations_map = game_durations.lock().await;
    for row in rows {
        let id: Option<i32> = Some(row.id.clone());
        if id.is_some() {
            durations_map.insert(
                id.unwrap(),
                row.duration.clone(),
            );
        }
    }
    Ok(())
}

pub async fn rd_verify_session(
    redis_client: Arc<Client>,
    session_id: &str,
    client_ip: &str,
) -> Result<bool, redis::RedisError> {
    // Get an async connection to Redis
    let mut conn = redis_client.get_multiplexed_async_connection().await?;

    // Retrieve the session details from Redis
    let session_key = format!("user_session:{}", session_id);
    let stored_client_ip: Option<String> = conn.hget(&session_key, "client_ip").await?;

    // Verify if the session exists and matches the client IP
    if let Some(stored_ip) = stored_client_ip {
        if stored_ip == client_ip {
            return Ok(true);
        }
    }

    Ok(false) // Session not found or IP mismatch
}

pub async fn rd_store_game_data(
    redis_client: Arc<Client>,
    session_id: &str,
    game_data: &str,
) -> Result<(), redis::RedisError> {
    // Get an async connection to Redis
    let mut conn = redis_client.get_multiplexed_async_connection().await?;

    // Store the game data in Redis
    let game_key = format!("game_data:{}", session_id);
    conn.set::<_, _, ()>(&game_key, game_data).await?;

    Ok(())
}