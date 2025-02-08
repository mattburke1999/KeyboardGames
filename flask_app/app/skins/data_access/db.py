from app.data_access.db import BaseDB
import psycopg2 as pg

from app.skins.data_access.models import Skin
from app.skins.data_access.models import Skins_Page
from app.skins.data_access.models import Skin_Input
from app.skins.data_access.models import Skin_Type_With_Inputs

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
        return Skins_Page(*result) if result else None
        
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
        return Skin(*result) if result else None
        
    def get_default_skin(self) -> Skin:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("select type, name, data from skins.skins_view where name = 'Black'")
                result = cur.fetchone()
        return Skin(*result) if result else None
            
    def set_user_skin(self, conn: pg.extensions.connection, user_id: int, skin_id: int) -> None:
        with conn.cursor() as cur:
            cur.execute('update accounts set skin_id = %s where id = %s', (skin_id, user_id))
        
    def check_skin_purchaseable(self, user_id: int, skin_id: int) -> bool:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select points <= (select points from skins.core where id = %s)
                    from accounts where id = %s
                ''', (skin_id, user_id))
                result = cur.fetchone()
        return result[0] if result else False
        
    def purchase_skin(self, conn: pg.extensions.connection, user_id: int, skin_id: int) -> None:
        with conn.cursor() as cur:
            cur.execute('select skins.purchase_skin(%s, %s)', (user_id, skin_id,))
        
    def get_skin_inputs(self) -> list[Skin_Input]:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select id, name from skins.inputs')
                results = cur.fetchall()
        return [Skin_Input(*res) for res in results] if results else None

    def get_skin_input_list(self, input_names: list[str]) -> dict[str, int]:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f"select json_object_agg(name, id) from skins.inputs where name in({', '.join(['%s'] * len(input_names))})", input_names)
                result = cur.fetchone()
        return result[0] if result else {}

    def get_skin_type_with_inputs(self) -> list[Skin_Type_With_Inputs]:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select t.id, t.name, jsonb_agg(i.name) inputs
                    from skins.types t
                    join skins.type_inputs ti on t.id = ti.type_id
                    join skins.inputs i on ti.input_id = i.id
                    group by t.name, t.id
                ''')
                results = cur.fetchall()
        return [Skin_Type_With_Inputs(*res) for res in results]
        
    def get_skin_input_id_by_name(self, name: str) -> int:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select id from skins.inputs where name = %s', (name,))
                result = cur.fetchone()
        return result[0] if result else None
        
    def new_skin_input(self, conn: pg.extensions.connection, name: str) -> int:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO skins.inputs (name) VALUES (%s) RETURNING id', (name,))
            result = cur.fetchone()
        return result[0] if result else None
        
    def create_skin_type(self, conn: pg.extensions.connection, type: str) -> int:
        with conn.cursor() as cur:
            cur.execute('insert into skins.types (name) values (%s) returning id', (type,))
            result = cur.fetchone()
        return result[0] if result else None
    
    def add_skin_type_inputs(self, conn: pg.extensions.connection, type_id: int, inputs: list[int]) -> None:
        with conn.cursor() as cur:
            cur.executemany('insert into skins.type_inputs (type_id, input_id) values (%s, %s)', [(type_id, input_id) for input_id in inputs])
        
    def check_skin_type_exists(self, name: str) -> bool:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select count(*) from skins.types where name = %s', (name,))
                result = cur.fetchone()
                return result[0] > 0 if result else False
        
    def new_skin(self, conn: pg.extensions.connection, name: str, points: int, type_id: int) -> int:
        with conn.cursor() as cur:
            cur.execute('INSERT into skins.core (name, points, type_id) VALUES (%s, %s, %s) RETURNING id', (name, points, type_id,))
            result = cur.fetchone()
        return result[0] if result else None
        
    def new_skin_values(self, conn: pg.extensions.connection, skin_id: int, input_id: int, value: str) -> None:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO skins.input_values (skin_id, input_id, value) VALUES (%s, %s, %s)', (skin_id, input_id, value))
        