import psycopg2 as pg
import os
import traceback
import bcrypt
from models import New_User
from models import Func_Result
from models import New_Skin

DATABASE_URL = None

def connect_db():
    global DATABASE_URL
    if not DATABASE_URL:
        DATABASE_URL = os.environ['DATABASE_URL']
    return pg.connect(DATABASE_URL)

def create_user(new_user: New_User) -> Func_Result:
    # first_name, last_name, username, email, password):
        with connect_db() as cnxn:
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

def check_user(username: str) -> Func_Result:
        try:
            with connect_db() as cnxn:
                with cnxn.cursor() as cursor:
                    cursor.execute('select id, password, isadmin from accounts where (email = %s or username = %s)', (username, username))
                    return Func_Result(True, cursor.fetchone())
        except:
            traceback.print_exc()
            return Func_Result(False, None)

def get_games() -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id, title, title_style, title_color, bg_rot, bg_color1, bg_color2, abbrev_name, duration, basic_circle_template from games order by id')
                return Func_Result(True, cur.fetchall())
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def check_unique_register_input(type: str, value: str) -> Func_Result:
    try:
        if type not in {'username', 'email'}:
            raise ValueError(f'Invalid type: {type}')
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f'SELECT count(*) from accounts where {type} = %s', (value,))
                result = cur.fetchone()
                if result:
                    return Func_Result(True, result[0] == 0)
                return Func_Result(False, None)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def get_profile(user_id: int) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select username, created_time, points, num_top10, ranks from profile_view where id = %s', (user_id,))
                return Func_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def update_score(user_id: int, game_id: int, score: int) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select high_scores, points_added, score_rank from update_scores(%s, %s, %s)', (user_id, game_id, score))
                result = cur.fetchone()
                conn.commit()
                return Func_Result(True, result)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def get_all_skins(user_id: int) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                        select points, skins
                        from (
                            select json_agg(json_build_object('id', s.id, 'type', s.type, 'name', s.name, 'data', s.data, 'points', s.points, 'user_choice', a.id is not null and a.id = %s, 'user_skin', us.id is not null and us.account_id = %s)) skins
                            from skins_view s
                            left join accounts a on s.id = a.skin_id and a.id = %s
                            left join user_skins us on s.id = us.skin_id and us.account_id = %s
                        ) s, accounts a 
                        where a.id = %s
                ''', (user_id, user_id, user_id, user_id, user_id))
                return Func_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def get_user_skin(user_id: int) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select type, name, data 
                    from skins_view s
                    join accounts a on s.id = a.skin_id
                    where a.id = %s
                ''', (user_id,))
                return Func_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def get_default_skin() -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("select type, name, data from skins_view where name = 'Black'")
                return Func_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def get_skin(skin_id: int) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select id, type, name, data from skins where id = %s', (skin_id,))
                return Func_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def set_user_skin(user_id: int, skin_id: int) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('update accounts set skin_id = %s where id = %s', (skin_id, user_id))
                conn.commit()
                return Func_Result(True, None)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def check_skin_purchaseable(user_id: int, skin_id: int) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select points <= (select points from skins where id = %s)
                    from accounts where id = %s
                ''', (skin_id, user_id))
                result = cur.fetchone()
                if result:
                    return Func_Result(True, result[0])
                return Func_Result(False, None)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def purchase_skin(user_id: int, skin_id: int) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select purchase_skin(%s, %s)', (user_id, skin_id,))
                return Func_Result(True, None)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def get_skin_inputs() -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select id, name from skin_inputs')
                return Func_Result(True, cur.fetchall())
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def get_skin_type_with_inputs() -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select t.id, t.name, jsonb_agg(i.name) inputs
                    from skin_types t
                    join skin_type_inputs ti on t.id = ti.type_id
                    join skin_inputs i on ti.input_id = i.id
                    group by t.name, t.id
                ''')
                return Func_Result(True, cur.fetchall())
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def get_skin_input_id_by_name(name: str) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select id from skin_inputs where name = %s', (name,))
                return Func_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def new_skin_input(conn: pg.extensions.connection, name: str) -> Func_Result:
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO skin_inputs (name) VALUES (%s) RETURNING id', (name,))
            result = cur.fetchone()
            if result:
                return Func_Result(True, result[0])
            return Func_Result(True, None)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def create_skin(conn: pg.extensions.connection, new_skin: New_Skin) -> Func_Result:
    try:
        with conn.cursor() as cur:
            cur.execute('insert into skin_types (name) values (%s) returning id', (new_skin.type,))
            type_id = cur.fetchone()
            if not type_id:
                return Func_Result(False, None)
            cur.executemany('insert into skin_type_inputs (type_id, input_id) values (%s, %s)', [(type_id, input_id) for input_id in new_skin.inputs])
        conn.commit()
        return Func_Result(True, type_id)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def check_skin_type_exists(name: str) -> Func_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select count(*) from skin_types where name = %s', (name,))
                result = cur.fetchone()
                if result:
                    return Func_Result(True, result[0]>0)
                return Func_Result(True, False)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def new_skin(conn: pg.extensions.connection, name: str, points: int, type_id: int ) -> Func_Result:
    try:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO skins (name, points, type_id) VALUES (%s, %s, %s) RETURNING id', (name, points, type_id,))
            result = cur.fetchone()
            if result:
                return Func_Result(True, result[0])
            return Func_Result(False, None)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    
def new_skin_values(conn: pg.extensions.connection, skin_id: int, input_id: int, value: str) -> Func_Result:
    try:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO skin_input_values (skin_id, input_id, value) VALUES (%s, %s, %s)', (skin_id, input_id, value,))
            return Func_Result(True, None)
    except:
        traceback.print_exc()
        return Func_Result(False, None)
    