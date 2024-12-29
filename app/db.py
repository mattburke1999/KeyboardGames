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
                cnxn.commit()
                return (True, result[0])
        except:
            traceback.print_exc()
            return (False, None)

def check_user(username):
        try:
            with connect_db() as cnxn:
                with cnxn.cursor() as cursor:
                    cursor.execute('select id, password from accounts where (email = %s or username = %s)', (username, username))
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
    
def update_score(user_id, game_id, score):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select * from update_scores(%s, %s, %s)', (user_id, game_id, score))
                results = cur.fetchall()
                conn.commit()
                return (True, results)
    except:
        traceback.print_exc()
        return (False, None)