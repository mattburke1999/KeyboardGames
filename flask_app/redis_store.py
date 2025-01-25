import redis
import uuid
from datetime import datetime
from datetime import timezone
import os

redis_client = redis.StrictRedis(host="localhost", password= os.environ.get('REDIS_PASSWORD'), port=6379, decode_responses=True)


def create_user_session(user_id, client_ip):
    try:
        # Generate a new session ID
        session_id = str(uuid.uuid4())
        issued_time = datetime.now(timezone.utc).isoformat()

        # Delete existing sessions for the user or IP
        clear_user_sessions(user_id, client_ip)

        # Create a new session in Redis
        redis_client.hset(f"user_session:{session_id}", mapping={
            "account_id": user_id,
            "client_ip": client_ip,
            "issued_time": issued_time
        })

        # Update the user session list (sorted by latest first)
        redis_client.lpush(f"user_sessions:{user_id}", session_id)

        return (True, session_id)
    except Exception as e:
        print(f"Error creating user session: {e}")
        return (False, None)
        
def clear_user_sessions(user_id, client_ip):
    try:
        existing_user_sessions = redis_client.lrange(f"user_sessions:{user_id}", 0, -1)    
        existing_ip_sessions = redis_client.lrange(f"user_sessions:{client_ip}", 0, -1)
        
        existing_sessions = set(existing_user_sessions + existing_ip_sessions)
        for session in existing_sessions:
            redis_client.delete(f"user_session:{session}")
            
        redis_client.delete(f"user_sessions:{user_id}")
        redis_client.delete(f"user_sessions:{client_ip}")
        return (True, None)
    except Exception as e:
        print(f"Error clearing user sessions: {e}")
        return (False, None)
    
def get_game_data(session_jwt):
    try: 
    #     let game_key = format!("game_data:{}", session_id);
    # conn.set(&game_key, game_data).await?;
        game_data = redis_client.get(f"game_data:{session_jwt}")
        return (True, game_data)
    except Exception as e:
        print(f"Error getting game data: {e}")
        return (False, None)