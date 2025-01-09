use sqlx::PgPool;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;
use serde_json::Value;

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

pub async fn update_score (
    pool: &PgPool,
    user_id: u32,
    score: u32,
    game_id: u32
) -> Result<(Vec<Value>, i32, i32), sqlx::Error> {
    let row = sqlx::query!(
        "SELECT high_scores, points_added, score_rank from update_scores($1, $2, $3)",
        user_id as i32,
        game_id as i32,
        score as i32
    )
    .fetch_one(pool)
    .await?;
    if let (Some(high_scores), Some(points_added), Some(score_rank)) = (row.high_scores, row.points_added, row.score_rank) {
        let high_scores: Vec<Value> = serde_json::from_value(high_scores)
            .map_err(|err| sqlx::Error::Decode(Box::new(err)))?;
        return Ok((high_scores, points_added, score_rank));
    } else {
        return Err(sqlx::Error::RowNotFound);
    }
}

pub async fn verify_session_and_get_userid (
    pool: &PgPool,
    session_id: &str,
) -> Result<u32, sqlx::Error> {
    let row = sqlx::query!(
        "SELECT account_id from user_sessions where session_id = $1",
        uuid::Uuid::parse_str(session_id).map_err(|err| sqlx::Error::Decode(Box::new(err)))?
    )
    .fetch_one(pool)
    .await?;
    if let Some(user_id) = row.account_id {
        return Ok(user_id as u32);
    } else {
        return Err(sqlx::Error::RowNotFound);
    }
}