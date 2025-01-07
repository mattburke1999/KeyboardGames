mod routes; // Enable routes module
mod sockets;
mod state;
mod db;

use warp::Filter;
use sqlx::PgPool;
use dotenv::dotenv;
use std::env;
use tokio::sync::Mutex;
use std::sync::Arc;
use crate::db::load_game_durations;
use crate::routes::endpoints::handle_endpoints;
use crate::state::PoolValue;
use crate::state::AppState;

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {
    dotenv().ok();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = PgPool::connect(&database_url).await?;

    // Initialize shared state
    let state = state::AppState::new();
    // set "pg_pool" to pool
    state.pg_pool = Arc::new(Mutex::new(state::PoolValue::Pool(pool)));

    load_game_durations(&pool, state.game_durations.clone()).await?;

    println!("{:?}", state.game_durations.lock().await);

    // Define the WebSocket route
    let ws_route = warp::path("ws")
        .and(warp::ws())
        .and(with_state(state.clone()))
        .map(|ws: warp::ws::Ws, state| {
            ws.on_upgrade(move |socket| sockets::handle_ws(socket, state))
        });

    // Import and define the API routes from `routes::endpoints`
    let api_routes = handle_endpoints(state.clone());

    // Combine WebSocket and API routes
    let routes = ws_route
        .or(api_routes)
        .with(warp::cors().allow_any_origin());

    // Start the Warp server
    let port = env::var("PORT").unwrap_or_else(|_| "3030".to_string()).parse::<u16>().unwrap();
    println!("Server running on port {}", port);

    warp::serve(routes)
        .run(([127, 0, 0, 1], port))
        .await;

    Ok(())
}

fn with_state(
    state: state::AppState,
) -> impl Filter<Extract = (state::AppState,), Error = std::convert::Infallible> + Clone {
    warp::any().map(move || state.clone())
}
