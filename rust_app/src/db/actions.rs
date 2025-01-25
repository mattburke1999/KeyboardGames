use sqlx::PgPool;
use std::collections::HashMap;
use std::sync::Arc;
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



pub async fn db_verify_session (
    pool: &PgPool,
    session_id: &str,
    client_ip: &str,
) -> Result<bool, sqlx::Error> {
    let row = sqlx::query!(
        "select exists(select 1 from user_sessions where session_id = $1 and client_ip = $2) as exists",
        // Convert the session_id to a UUID, and pass client_ip as a string
        uuid::Uuid::parse_str(session_id).map_err(|err| sqlx::Error::Decode(Box::new(err)))?,
        client_ip
    )
    .fetch_one(pool)
    .await?;
    if let Some(exists) = row.exists {
        return Ok(exists);
    } else {
        return Err(sqlx::Error::RowNotFound);
    }
}