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
    
def create_user_session(user_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('delete from user_sessions where account_id = %s', (user_id,))
                cur.execute('insert into user_sessions (account_id) values (%s) returning session_id', (user_id,))
                return (True, cur.fetchone()[0])
    except:
        conn.rollback()
        traceback.print_exc()
        return (False, None)
    
def get_user_session(user_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('select session_id from user_sessions where account_id = %s order by issued_time desc limit 1', (user_id,))
                return (True, cur.fetchone())
    except:
        traceback.print_exc()
        return (False, None)
    
def clear_user_sessions(user_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('delete from user_sessions where account_id = %s', (user_id,))
                return (True, None)
    except:
        traceback.print_exc()
        return (False, None)
    
def get_profile(user_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    with score_ranks as (
                        select account_id,
                            game_id, 
                            score,
                            row_number() over (partition by game_id order by score desc, score_date desc) "rank"
                        from scores
                    )
                    select username, created_time, points, num_top10, json_agg(json_build_object('score', score, 'rank', s.rank, 'game_name', g.title)) as ranks
                    from (
                        select min(rank) "rank", game_id, account_id
                        from score_ranks s
                        where account_id = %s
                            and rank <= 3
                        group by game_id, account_id
                    ) s
                    join score_ranks sr on sr.game_id = s.game_id and sr.account_id = s.account_id and sr.rank = s.rank
                    join games g on g.id = s.game_id
                    join (
                        select account_id, 
                            sum(case when rank <= 10 then 1 else 0 end) as num_top10
                        from score_ranks	
                        group by account_id
                    ) s2 on s.account_id = s2.account_id
                    join accounts a on a.id = s.account_id
                    where a.id = %s
                    group by username, created_time, num_top10, points
                ''', (user_id, user_id))
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
                            select json_agg(json_build_object('type', s.type, 'name', s.name, 'data', s.data, 'points', s.points, 'user_choice', a.id is not null and a.id = %s, 'user_skin', us.id is not null and us.account_id = %s)) skins
                            from skins s
                            left join accounts a on s.id = a.skin_id and a.id = %s
                            left join user_skins us on s.id = us.skin_id and us.account_id = %s
                        ) s, accounts a 
                        where a.id = %s
                ''', (user_id, user_id, user_id, user_id, user_id))
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