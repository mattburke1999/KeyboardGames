mod routes;

use routes::endpoints;

let api_routes = endpoints::endpoints(state.clone());

// Combine WebSocket and API routes
let routes = ws_route
    .or(api_routes)
    .with(warp::cors().allow_any_origin());