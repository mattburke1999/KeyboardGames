use jsonwebtoken::{decode, DecodingKey, Validation, Algorithm, TokenData};
use serde::{Deserialize, Serialize};
use std::env;
use warp::reject;

use crate::state::PoolValue;
use crate::state::AppState;
use crate::db::db_verify_session;

#[derive(Debug)]
pub enum UtilError
{
    StringError(String),
    InvalidPoolTypeError(InvalidPoolType),

}

#[derive(Debug)]
pub struct InvalidPoolType;

impl reject::Reject for InvalidPoolType {}

#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    session_jwt: String,
    client_ip: String,
    exp: usize,
}


#[derive(Debug)]
pub struct TokenResponse {
    pub session_id: String,
    pub client_ip: String,
    pub decoded: bool,
}

pub fn decode_session_token(token: &str) -> TokenResponse {
    let secret_key = env::var("SHARED_SECRET_KEY").expect("SHARED_SECRET_KEY must be set");

    // Define validation settings, disabling the requirement for the `exp` claim
    let mut validation = Validation::new(Algorithm::HS256);
    validation.validate_exp = true;
    validation.leeway = 5;

    // Decode the token
    let decoded: Result<TokenData<Claims>, jsonwebtoken::errors::Error> = decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret_key.as_ref()),
        &validation,
    );
    match decoded {
        Ok(data) => {
            println!("Token is valid!");
            println!("Session JWT: {:?}", data.claims.session_jwt);
            return TokenResponse {
                session_id: data.claims.session_jwt,
                client_ip: data.claims.client_ip,
                decoded: true,
            };
        }
        Err(err) => {
            println!("Failed to decode token: {}", err);
            return TokenResponse {
                session_id: "".to_string(),
                client_ip: "".to_string(),
                decoded: false,
            };
        }
    }
}


pub async fn verify_session(session_id: &str, client_ip: &str, client_ip_port: &str, state: &AppState) -> Result<bool, UtilError> {
    // Verify the session_id return true or false
    let actual_ip = client_ip_port.split(":").collect::<Vec<&str>>()[0];
    if actual_ip == client_ip {
        let pg_pool = state.pg_pool.clone();
        let pool = pg_pool.lock().await;

        if let PoolValue::Pool(ref pg_pool) = *pool {
            let session_exists = db_verify_session(&pg_pool, &session_id, &client_ip).await;
            if session_exists.is_ok() {
                return Ok(true);
            } else {
                return Err(UtilError::StringError("User not found".to_string()));
            }
        } else {
            // Handle the case where the PoolValue is not a PgPool
            return Err(UtilError::InvalidPoolTypeError(InvalidPoolType));
        }
    } else {
        return Err(UtilError::StringError("Client IP does not match".to_string()));
    }
}
