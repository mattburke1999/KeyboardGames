from app.data_access.db import BaseDB

from app.auth.data_access.models import New_User
from app.auth.data_access.models import Profile

import psycopg2 as pg
import bcrypt

class AuthDB(BaseDB):
    
    def create_user(self, conn: pg.extensions.connection, new_user: New_User) -> int | None:
        with conn.cursor() as cursor:
            cursor.execute('insert into accounts (first_name, last_name, username, email, password) values (%s, %s, %s, %s, %s) returning id', (new_user.first_name, new_user.last_name, new_user.username, new_user.email, bcrypt.hashpw(new_user.password.encode('utf-8'), bcrypt.gensalt())))
            result = cursor.fetchone()
            return result[0] if result else None
        
    def add_default_skin(self, conn: pg.extensions.connection, user_id: int) -> None:
        with conn.cursor() as cursor:
            cursor.execute('insert into user_skins (account_id, skin_id) values (%s, 1)', (user_id,))
    
    def check_user(self, username: str) -> tuple[int, bytes, bool] | tuple[None, None, None]:
        with self.connect_db() as cnxn:
            with cnxn.cursor() as cursor:
                cursor.execute('select id, password, isadmin from accounts where (email = %s or username = %s)', (username, username))
                result = cursor.fetchone()
                return result if result else (None, None, None)

    def check_unique_register_input(self, type: str, value: str) -> bool:
        if type not in {'username', 'email'}:
            raise ValueError(f'Invalid type: {type}')
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f'SELECT count(*) from accounts where {type} = %s', (value,))
                result = cur.fetchone()
                return result[0] == 0 if result else True
        
    def get_profile(self, user_id: int) -> Profile | None:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select username, created_time, points, num_top10, ranks from profile_view where id = %s', (user_id,))
                result = cur.fetchone()
                return Profile(*result) if result else None
    