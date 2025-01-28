import psycopg2 as pg
import os
import traceback
import bcrypt
from models import NewUser
from models import DB_Result

DATABASE_URL = None

def connect_db():
    global DATABASE_URL
    if not DATABASE_URL:
        DATABASE_URL = os.environ['DATABASE_URL']
    return pg.connect(DATABASE_URL)

def create_user(new_user: NewUser) -> DB_Result:
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
                        return DB_Result(True, result[0])
                    cnxn.rollback()
                    return DB_Result(False, None)
            # (True, result[0])
            except:
                cnxn.rollback()
                traceback.print_exc()
                return DB_Result(False, None)

def check_user(username: str) -> DB_Result:
        try:
            with connect_db() as cnxn:
                with cnxn.cursor() as cursor:
                    cursor.execute('select id, password, isadmin from accounts where (email = %s or username = %s)', (username, username))
                    return DB_Result(True, cursor.fetchone())
        except:
            traceback.print_exc()
            return DB_Result(False, None)

def get_games() -> DB_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id, title, title_style, title_color, bg_rot, bg_color1, bg_color2, abbrev_name, duration, basic_circle_template from games order by id')
                return DB_Result(True, cur.fetchall())
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def check_unique_register_input(type: str, value: str) -> DB_Result:
    try:
        if type not in {'username', 'email'}:
            raise ValueError(f'Invalid type: {type}')
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f'SELECT count(*) from accounts where {type} = %s', (value,))
                result = cur.fetchone()
                if result:
                    return DB_Result(True, result[0] == 0)
                return DB_Result(False, None)
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def get_profile(user_id: int) -> DB_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select username, created_time, points, num_top10, ranks from profile_view where id = %s', (user_id,))
                return DB_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def update_score(user_id: int, game_id: int, score: int) -> DB_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select high_scores, points_added, score_rank from update_scores(%s, %s, %s)', (user_id, game_id, score))
                result = cur.fetchone()
                conn.commit()
                return DB_Result(True, result)
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def get_all_skins(user_id: int) -> DB_Result:
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
                return DB_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def get_user_skin(user_id: int) -> DB_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select type, name, data 
                    from skins_view s
                    join accounts a on s.id = a.skin_id
                    where a.id = %s
                ''', (user_id,))
                return DB_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def get_default_skin() -> DB_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("select type, name, data from skins_view where name = 'Black'")
                return DB_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def get_skin(skin_id: int) -> DB_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select id, type, name, data from skins where id = %s', (skin_id,))
                return DB_Result(True, cur.fetchone())
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def set_user_skin(user_id: int, skin_id: int) -> DB_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('update accounts set skin_id = %s where id = %s', (skin_id, user_id))
                conn.commit()
                return DB_Result(True, None)
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def check_skin_purchaseable(user_id: int, skin_id: int) -> DB_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select points <= (select points from skins where id = %s)
                    from accounts where id = %s
                ''', (skin_id, user_id))
                result = cur.fetchone()
                if result:
                    return DB_Result(True, result[0])
                return DB_Result(False, None)
    except:
        traceback.print_exc()
        return DB_Result(False, None)
    
def purchase_skin(user_id: int, skin_id: int) -> DB_Result:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select purchase_skin(%s, %s)', (user_id, skin_id,))
                return DB_Result(True, None)
    except:
        traceback.print_exc()
        return DB_Result(False, None)