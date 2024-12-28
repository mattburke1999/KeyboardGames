import psycopg2 as pg
import os
import traceback

DATABASE_URL = None

def connect_db():
    global DATABASE_URL
    if not DATABASE_URL:
        DATABASE_URL = os.environ['DATABASE_URL']
    return pg.connect(DATABASE_URL)

def get_games():
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id, title, title_style, title_color, bg_rot, bg_color1, bg_color2, abbrev_name, duration, basic_circle_template from games')
                return (True, cur.fetchall())
    except:
        traceback.print_exc()
        return (False, None)