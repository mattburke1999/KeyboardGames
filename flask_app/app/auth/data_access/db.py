from app.data_access.db import BaseDB

from app.data_access.models import Func_Result
from app.auth.data_access.models import New_User
from app.auth.data_access.models import Profile

import traceback
import bcrypt

class AuthDB(BaseDB):
    def create_user(self, new_user: New_User) -> Func_Result:
        # first_name, last_name, username, email, password):
            with self.connect_db() as cnxn:
                try:
                    with cnxn.cursor() as cursor:
                        cursor.execute('insert into accounts (first_name, last_name, username, email, password) values (%s, %s, %s, %s, %s) returning id', (new_user.first_name, new_user.last_name, new_user.username, new_user.email, bcrypt.hashpw(new_user.password.encode('utf-8'), bcrypt.gensalt())))
                            # first_name, last_name, username, email, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())))
                        result = cursor.fetchone()
                        if result:
                            cursor.execute('insert into user_skins (account_id, skin_id) values (%s, 1)', (result[0],))
                            cnxn.commit()
                            return Func_Result(True, result[0])
                        cnxn.rollback()
                        return Func_Result(False, None)
                # (True, result[0])
                except:
                    cnxn.rollback()
                    traceback.print_exc()
                    return Func_Result(False, None)

    def check_user(self, username: str) -> Func_Result:
            try:
                with self.connect_db() as cnxn:
                    with cnxn.cursor() as cursor:
                        cursor.execute('select id, password, isadmin from accounts where (email = %s or username = %s)', (username, username))
                        return Func_Result(True, cursor.fetchone())
            except:
                traceback.print_exc()
                return Func_Result(False, None)

    def check_unique_register_input(self, type: str, value: str) -> bool:
        if type not in {'username', 'email'}:
            raise ValueError(f'Invalid type: {type}')
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f'SELECT count(*) from accounts where {type} = %s', (value,))
                result = cur.fetchone()
                return result[0] == 0 if result else True
        
    def get_profile(self, user_id: int) -> Profile:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select username, created_time, points, num_top10, ranks from profile_view where id = %s', (user_id,))
                result = cur.fetchone()
                return Profile(result[0], result[1], result[2], result[3], result[4]) if result else None
    