from app.data_access.db import BaseDB
from .models import Profile

class ProfileDB(BaseDB):
    
    def get_profile(self, user_id: int) -> Profile | None:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select username, created_time, points, num_top10, ranks from profile_view where id = %s', (user_id,))
                result = cur.fetchone()
                return Profile(*result) if result else None