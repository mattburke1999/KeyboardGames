// mod sockets;
// mod routes;
mod state;
mod db;

use warp::Filter;
use sqlx::PgPool;
use dotenv::dotenv;
use std::env;
use crate::db::load_game_metadata;

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {

    dotenv().ok();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = PgPool::connect(&database_url).await?;

    // Initialize shared state
    let state = state::AppState::new();

    load_game_metadata(&pool, state.game_metadata.clone()).await?;

    println!("{:?}", state.game_metadata.lock().unwrap());

    Ok(())
}