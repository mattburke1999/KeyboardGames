// mod sockets;
// mod routes;
mod state;
mod db;

use warp::Filter;
use sqlx::PgPool;
use dotenv::dotenv;
use std::env;
use crate::db::load_game_durations;

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {

    dotenv().ok();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = PgPool::connect(&database_url).await?;

    // Initialize shared state
    let state = state::AppState::new();

    load_game_durations(&pool, state.game_durations.clone()).await?;

    println!("{:?}", state.game_durations.lock().unwrap());

    Ok(())
}