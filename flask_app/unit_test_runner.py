from unit_test_rv import run_tests
from unit_test_rv import view_tests
import psycopg2 as pg
import sys
from dotenv import load_dotenv
import os
load_dotenv(override=True)

CNXN_STRING = os.getenv('DATABASE_URL')
TEST_CNXN_STRING = os.getenv('TEST_DATABASE_URL')

SQL_CREATE = r'db_files\games_table.sql'

def connect_db():
    conn = pg.connect(CNXN_STRING)
    return conn

def test_connect_db():
    conn = pg.connect(TEST_CNXN_STRING)
    return conn

def all_test_setup():
    sql_create_script = None
    with open(SQL_CREATE, 'r') as file:
        sql_create_script = file.read()
    if sql_create_script is None:
        raise Exception('Could not read sql script')
    print('Starting database setup')
    live_db_conn = connect_db()
    live_db_conn.autocommit = True
    with live_db_conn.cursor() as cur:
        cur.execute('create database keyboard_games_test;')
    live_db_conn.close()
    print('Database created')
    with test_connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_create_script)
        conn.commit()
    print('Database setup complete')
    
def all_test_teardown():
    print('Starting database teardown')
    live_db_conn = connect_db()
    live_db_conn.autocommit = True
    with live_db_conn.cursor() as cur:
        cur.execute('drop database keyboard_games_test;')
    live_db_conn.close()
    print('Database teardown complete')


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '-view':
        view_tests(CNXN_STRING) # type: ignore
    else:
        save_to_db = True if args and args[0] == '-save' else False
        run_tests(CNXN_STRING, 'flask_app', save_to_db=save_to_db, tests_setup_func=all_test_setup, tests_teardown_func=all_test_teardown) # type: ignore