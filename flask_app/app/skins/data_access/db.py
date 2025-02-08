from app.data_access.db import BaseDB
import psycopg2 as pg

import traceback
from app.data_access.models import Func_Result
from app.skins.data_access.models import New_Skin_Type
from app.skins.data_access.models import Skin
from app.skins.data_access.models import Skins_Page

class SkinDB(BaseDB):
    def get_all_skins(self, user_id: int) -> Skins_Page:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                        select points, skins
                        from (
                            select json_agg(json_build_object('id', s.id, 'type', s.type, 'name', s.name, 'data', s.data, 'points', s.points, 'user_choice', a.id is not null and a.id = %s, 'user_skin', us.id is not null and us.account_id = %s)) skins
                            from skins.skins_view s
                            left join accounts a on s.id = a.skin_id and a.id = %s
                            left join user_skins us on s.id = us.skin_id and us.account_id = %s
                        ) s, accounts a 
                        where a.id = %s
                ''', (user_id, user_id, user_id, user_id, user_id))
                result = cur.fetchone()
        return Skins_Page(result[0], result[1]) if result else None
        
    def get_user_skin(self, user_id: int) -> Skin:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select type, name, data 
                    from skins.skins_view s
                    join accounts a on s.id = a.skin_id
                    where a.id = %s
                ''', (user_id,))
                result = cur.fetchone()
        return Skin(result[0], result[1], result[2]) if result else None
        
    def get_default_skin(self) -> Skin:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("select type, name, data from skins.skins_view where name = 'Black'")
                result = cur.fetchone()
        return Skin(result[0], result[1], result[2]) if result else None
            
    def set_user_skin(self, user_id: int, skin_id: int) -> Func_Result:
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute('update accounts set skin_id = %s where id = %s', (skin_id, user_id))
                    conn.commit()
                    return Func_Result(True, None)
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        
    def check_skin_purchaseable(self, user_id: int, skin_id: int) -> Func_Result:
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        select points <= (select points from skins.core where id = %s)
                        from accounts where id = %s
                    ''', (skin_id, user_id))
                    result = cur.fetchone()
                    if result:
                        return Func_Result(True, result[0])
                    return Func_Result(False, None)
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        
    def purchase_skin(self, user_id: int, skin_id: int) -> Func_Result:
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute('select skins.purchase_skin(%s, %s)', (user_id, skin_id,))
                    return Func_Result(True, None)
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        
    def get_skin_inputs(self) -> Func_Result:
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute('select id, name from skins.inputs')
                    return Func_Result(True, cur.fetchall())
        except:
            traceback.print_exc()
            return Func_Result(False, None)

    def get_skin_input_list(self, input_names: list[str]) -> Func_Result:
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"select id, name from skins.inputs where name in({', '.join(['%s'] * len(input_names))})", input_names)
                    return Func_Result(True, cur.fetchall())
        except:
            traceback.print_exc()
            return Func_Result(False, None)

    def get_skin_type_with_inputs(self) -> Func_Result:
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        select t.id, t.name, jsonb_agg(i.name) inputs
                        from skins.types t
                        join skins.type_inputs ti on t.id = ti.type_id
                        join skins.inputs i on ti.input_id = i.id
                        group by t.name, t.id
                    ''')
                    return Func_Result(True, cur.fetchall())
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        
    def get_skin_input_id_by_name(self, name: str) -> Func_Result:
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute('select id from skins.inputs where name = %s', (name,))
                    return Func_Result(True, cur.fetchone())
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        
    def new_skin_input(self, conn: pg.extensions.connection, name: str) -> Func_Result:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO skins.inputs (name) VALUES (%s) RETURNING id', (name,))
                result = cur.fetchone()
                if result:
                    return Func_Result(True, result[0])
                return Func_Result(True, None)
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        
    def create_skin_type(self, conn: pg.extensions.connection, new_skin: New_Skin_Type) -> Func_Result:
        try:
            with conn.cursor() as cur:
                cur.execute('insert into skins.types (name) values (%s) returning id', (new_skin.type,))
                type_id = cur.fetchone()
                if not type_id:
                    return Func_Result(False, None)
                cur.executemany('insert into skins.type_inputs (type_id, input_id) values (%s, %s)', [(type_id, input_id) for input_id in new_skin.inputs])
            conn.commit()
            return Func_Result(True, type_id)
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        
    def check_skin_type_exists(self, name: str) -> Func_Result:
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute('select count(*) from skins.types where name = %s', (name,))
                    result = cur.fetchone()
                    if result:
                        return Func_Result(True, result[0]>0)
                    return Func_Result(True, False)
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        
    def new_skin(self, conn: pg.extensions.connection, name: str, points: int, type_id: int ) -> Func_Result:
        try:
            with conn.cursor() as cur:
                cur.execute('INSERT into skins.core (name, points, type_id) VALUES (%s, %s, %s) RETURNING id', (name, points, type_id,))
                result = cur.fetchone()
                if result:
                    return Func_Result(True, result[0])
                return Func_Result(False, None)
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        
    def new_skin_values(self, conn: pg.extensions.connection, skin_id: int, input_id: int, value: str) -> Func_Result:
        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO skins.input_values (skin_id, input_id, value) VALUES (%s, %s, %s)', (skin_id, input_id, value,))
                return Func_Result(True, None)
        except:
            traceback.print_exc()
            return Func_Result(False, None)
        