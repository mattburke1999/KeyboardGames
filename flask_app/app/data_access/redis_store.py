import redis
import uuid
from datetime import datetime
from datetime import timezone
import json
from app.games.data_access.models import Game_Data

class Redis_Store():
    redis_client = None
    
    @classmethod
    def initialize(cls, host: str, port: int, password: str):
        cls.redis_client = redis.StrictRedis(host=host, password=password, port=port, decode_responses=True)
        
    def create_user_session(self, user_id: int, client_ip: str) -> str:
            # Generate a new session ID
        session_id = str(uuid.uuid4())
        issued_time = datetime.now(timezone.utc).isoformat()

        # Delete existing sessions for the user or IP
        self.clear_user_sessions(user_id, client_ip)

        # Create a new session in Redis
        self.redis_client.hset(f"user_session:{session_id}", mapping={ # type: ignore
            "account_id": user_id,
            "client_ip": client_ip,
            "issued_time": issued_time
        })

        # Update the user session list (sorted by latest first)
        self.redis_client.lpush(f"user_sessions:{user_id}", session_id) # type: ignore

        return session_id
            
    def clear_user_sessions(self, user_id: int, client_ip: str) -> None:
        existing_user_sessions = self.redis_client.lrange(f"user_sessions:{user_id}", 0, -1) # type: ignore
        existing_ip_sessions = self.redis_client.lrange(f"user_sessions:{client_ip}", 0, -1) # type: ignore
        
        existing_sessions = set(existing_user_sessions + existing_ip_sessions) # type: ignore
        for session in existing_sessions:
            self.redis_client.delete(f"user_session:{session}") # type: ignore
            
        self.redis_client.delete(f"user_sessions:{user_id}") # type: ignore
        self.redis_client.delete(f"user_sessions:{client_ip}") # type: ignore
        
    def get_game_data(self, session_jwt: str) -> Game_Data | None:
        result = self.redis_client.get(f"game_data:{session_jwt}") # type: ignore
        return Game_Data(**json.loads(result)) if result else None # type: ignore