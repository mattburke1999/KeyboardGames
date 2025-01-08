use jsonwebtoken::{decode, DecodingKey, Validation, Algorithm, TokenData};
use serde::{Deserialize, Serialize};
use std::env;

use crate::state::PoolValue;
use crate::state::AppState;

#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    session_id: String,
}

fn decode_session_token(token: &str) -> Result<String, jsonwebtoken::errors::Error> {
    let secret_key = env::var("SHARED_SECRET_KEY").expect("SHARED_SECRET_KEY must be set");

    // Define validation settings, disabling the requirement for the `exp` claim
    let mut validation = Validation::new(Algorithm::HS256);
    validation.validate_exp = false;
    validation.required_spec_claims.clear();

    // Decode the token
    let decoded: Result<TokenData<Claims>, jsonwebtoken::errors::Error> = decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret_key.as_ref()),
        &validation,
    );

    // Return the session_id or an error
    decoded.map(|data| data.claims.session_id)
}

async fn convert_jwt_to_user_id(user_jwt: &str, state: AppState) -> Result<u32, jsonwebtoken::errors::Error> {
    match decode_session_token(user_jwt) {
        //proceed with session_id
        Ok(session_id) => {
            let pg_pool = state.pg_pool.clone();
            let pool = pg_pool.lock().await;

            if let PoolValue::Pool(ref pg_pool) = *pool {
                let user_id = verify_session_and_get_userid(&pg_pool, &session_id).await?;
                return Ok(user_id as u32);
            } else {
                // Handle the case where the PoolValue is not a PgPool
                return Err(warp::reject::custom(InvalidPoolType));
            }
        }
        //return error
        Err(e) => {
            eprintln!("Failed to decode session token: {}", e);
            return Err(e);
        }
    }
}

async fn verify_session(user_jwt: &str) -> Result<i32, jsonwebtoken::errors::Error> {
    // Verify the session_id return true or false
    match decode_session_token(user_jwt) {
        Ok(session_id) => {
            let pg_pool = state.pg_pool.clone();
            let pool = pg_pool.lock().await;

            if let PoolValue::Pool(ref pg_pool) = *pool {
                let user_id = verify_session_and_get_userid(&pg_pool, &session_id).await?;
                return Ok(True);
            } else {
                // Handle the case where the PoolValue is not a PgPool
                return Err(warp::reject::custom(InvalidPoolType));
            }
        }
        Err(e) => {
            eprintln!("Failed to decode session token: {}", e);
            return Err(e);
        }
    }
}