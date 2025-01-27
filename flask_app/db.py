import psycopg2 as pg
import os
import traceback
import bcrypt

DATABASE_URL = None

def connect_db():
    global DATABASE_URL
    if not DATABASE_URL:
        DATABASE_URL = os.environ['DATABASE_URL']
    return pg.connect(DATABASE_URL)

def create_user(first_name, last_name, username, email, password):
        try:
            with connect_db() as cnxn:
                with cnxn.cursor() as cursor:
                    cursor.execute('insert into accounts (first_name, last_name, username, email, password) values (%s, %s, %s, %s, %s) returning id', (first_name, last_name, username, email, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())))
                    result = cursor.fetchone()
                    cursor.execute('insert into user_skins (account_id, skin_id) values (%s, 1)', (result[0],))
                cnxn.commit()
                return (True, result[0])
        except:
            cnxn.rollback()
            traceback.print_exc()
            return (False, None)

def check_user(username):
        try:
            with connect_db() as cnxn:
                with cnxn.cursor() as cursor:
                    cursor.execute('select id, password, isadmin from accounts where (email = %s or username = %s)', (username, username))
                    return (True, cursor.fetchone())
        except:
            traceback.print_exc()
            return (False, None)

def get_games():
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id, title, title_style, title_color, bg_rot, bg_color1, bg_color2, abbrev_name, duration, basic_circle_template from games order by id')
                return (True, cur.fetchall())
    except:
        traceback.print_exc()
        return (False, None)
    
def check_unique_register_input(type, value):
    try:
        if type not in {'username', 'email'}:
            raise ValueError(f'Invalid type: {type}')
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f'SELECT count(*) from accounts where {type} = %s', (value,))
                return (True, cur.fetchone()[0] == 0)
    except:
        traceback.print_exc()
        return (False, None)
    
def get_profile(user_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select username, created_time, points, num_top10, ranks from profile_view where id = %s', (user_id,))
                return (True, cur.fetchone())
    except:
        traceback.print_exc()
        return (False, None)
    
def update_score(user_id, game_id, score):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select high_scores, points_added, score_rank from update_scores(%s, %s, %s)', (user_id, game_id, score))
                results = cur.fetchone()
                conn.commit()
                return (True, results)
    except:
        traceback.print_exc()
        return (False, None)
    
def get_all_skins(user_id):
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
                return (True, cur.fetchone())
    except:
        traceback.print_exc()
        return (False, None)
    
def get_user_skin(user_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select type, name, data 
                    from skins_view s
                    join accounts a on s.id = a.skin_id
                    where a.id = %s
                ''', (user_id,))
                return (True, cur.fetchone())
    except:
        traceback.print_exc()
        return (False, None)
    
def get_default_skin():
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("select type, name, data from skins_view where name = 'Black'")
                return (True, cur.fetchone())
    except:
        traceback.print_exc()
        return (False, None)
    
def get_skin(skin_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select id, type, name, data from skins where id = %s', (skin_id,))
                return (True, cur.fetchone())
    except:
        traceback.print_exc()
        return (False, None)
    
def set_user_skin(user_id, skin_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('update accounts set skin_id = %s where id = %s', (skin_id, user_id))
                conn.commit()
                return (True, None)
    except:
        traceback.print_exc()
        return (False, None)
    
def check_skin_purchaseable(user_id, skin_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select points <= (select points from skins where id = %s)
                    from accounts where id = %s
                ''', (skin_id, user_id))
                return (True, cur.fetchone()[0])
    except:
        traceback.print_exc()
        return (False, None)
    
def purchase_skin(user_id, skin_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select purchase_skin(%s, %s)', (user_id, skin_id,))
                return (True, None)
    except:
        traceback.print_exc()
        return (False, None)