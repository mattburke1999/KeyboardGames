import redis
import uuid
from datetime import datetime
from datetime import timezone
import os
import json
from app.games.models import Game_Data

redis_client = redis.StrictRedis(host="localhost", password= os.environ.get('REDIS_PASSWORD'), port=6379, decode_responses=True)


def create_user_session(user_id: int, client_ip: str) -> str:
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

    return session_id
        
def clear_user_sessions(user_id: int, client_ip: str) -> None:
    existing_user_sessions = redis_client.lrange(f"user_sessions:{user_id}", 0, -1)    
    existing_ip_sessions = redis_client.lrange(f"user_sessions:{client_ip}", 0, -1)
    
    existing_sessions = set(existing_user_sessions + existing_ip_sessions) # type: ignore
    for session in existing_sessions:
        redis_client.delete(f"user_session:{session}")
        
    redis_client.delete(f"user_sessions:{user_id}")
    redis_client.delete(f"user_sessions:{client_ip}")
    
def get_game_data(session_jwt: str) -> Game_Data:
    result = redis_client.get(f"game_data:{session_jwt}")
    return Game_Data(**json.loads(result)) if result else None