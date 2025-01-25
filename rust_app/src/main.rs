mod routes;
mod sockets;
mod state;
mod db;
mod utils;

use warp::Filter;
use sqlx::PgPool;
use dotenv::dotenv;
use std::env;
use tokio::sync::Mutex;
use redis::Client;
use std::sync::Arc;
use std::net::SocketAddr;

use crate::db::load_game_durations;
use crate::routes::endpoints::handle_endpoints;


fn cors_config() -> warp::cors::Cors {
    warp::cors()
        .allow_origin("http://localhost:5000") // Allow localhost
        .allow_origin("http://127.0.0.1:5000") // Allow 127.0.0.1
        .allow_origin("http://192.168.1.125:5000")
        .allow_origin("http://192.168.1.177:5000")
        .allow_methods(vec!["GET", "POST"]) // Allow specific HTTP methods
        .allow_headers(vec!["Content-Type", "Authorization"]) // Allow specific headers
        .build()
}


#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {
    dotenv().ok();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = PgPool::connect(&database_url).await?;
    let redis_password = env::var("REDIS_PASSWORD").expect("REDIS_PASSWORD must be set");
    let redis_url = format!("redis://:{}@127.0.0.1:6379/", redis_password);
    let redis_client = Arc::new(
        Client::open(redis_url).expect("Failed to create Redis client")
    );

    // Initialize shared state
    let mut state = state::AppState::new(redis_client.clone());
    state.pg_pool = Arc::new(Mutex::new(state::PoolValue::Pool(pool.clone())));

    load_game_durations(&pool, state.game_durations.clone()).await?;

    println!("{:?}", state.game_durations.lock().await);

    // Define the WebSocket route
    let ws_route = warp::path("ws")
        .and(warp::ws())
        .and(warp::addr::remote())
        .and(with_state(state.clone()))
        .map(|ws: warp::ws::Ws, addr: Option<SocketAddr>, state| {
            ws.on_upgrade(move |socket| {
                // Pass the client's address to the WebSocket handler
                sockets::handle_ws(socket, addr, state)
            })
        });

    // Import and define the API routes from `routes::endpoints`
    let api_routes = handle_endpoints(state.clone());

    // Combine WebSocket and API routes
    let routes = ws_route
        .or(api_routes)
        .with(cors_config()); // Apply CORS configuration

    // Start the Warp server
    let port = env::var("PORT").unwrap_or_else(|_| "3030".to_string()).parse::<u16>().unwrap();
    println!("Server running on port {}", port);

    warp::serve(routes)
        .run(([0, 0, 0, 0], port))
        .await;

    Ok(())
}

fn with_state(
    state: state::AppState,
) -> impl Filter<Extract = (state::AppState,), Error = std::convert::Infallible> + Clone {
    warp::any().map(move || state.clone())
}
