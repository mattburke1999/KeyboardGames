use sqlx::PgPool;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

pub async fn load_game_durations(
    pool: &PgPool,
    game_durations: Arc<Mutex<HashMap<i32, f64>>>,
) -> Result<(), sqlx::Error> {
    let rows = sqlx::query!("SELECT id, duration from games")
        .fetch_all(pool)
        .await?;
    
    let mut durations_map = game_durations.lock().unwrap();
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