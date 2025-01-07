use sqlx::PgPool;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;

pub async fn load_game_durations(
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
    user_id: i32,
    score: i32,
    game_id: i32
) -> Result<(Vec<i32>, i32, i32), sqlx::Error> {
    let row = sqlx::query!(
        "SELECT high_scores, points_added, score_rank from update_scores($1, $2, $3)",
        user_id,
        game_id,
        score
    )
    .fetch_one(pool)
    .await?;
    Ok((row.high_scores, row.points_added, row.score_rank))
}