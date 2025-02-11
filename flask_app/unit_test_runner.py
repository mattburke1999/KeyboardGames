import unittest
import xmlrunner
import psycopg2 as pg
from dotenv import load_dotenv
load_dotenv(override=True)
import os
from xml_to_html import convert_xml_to_html

sql_create = r'db_files\games_table.sql'

def all_test_setup():
    sql_create_script = None
    with open(sql_create, 'r') as file:
        sql_create_script = file.read()
    if sql_create_script is None:
        raise Exception('Could not read sql script')
    print('Starting database setup')
    live_db_conn = pg.connect(os.getenv('DATABASE_URL'))
    live_db_conn.autocommit = True
    with live_db_conn.cursor() as cur:
        cur.execute('create database keyboard_games_test;')
    live_db_conn.close()
    print('Database created')
    with pg.connect(os.getenv('TEST_DATABASE_URL')) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_create_script)
        conn.commit()
    print('Database setup complete')
    
def all_test_teardown():
    print('Starting database teardown')
    live_db_conn = pg.connect(os.getenv('DATABASE_URL'))
    live_db_conn.autocommit = True
    with live_db_conn.cursor() as cur:
        cur.execute('drop database keyboard_games_test;')
    live_db_conn.close()
    print('Database teardown complete')

def run_unit_tests():
    all_test_setup()

    try:
        test_folder = r'flask_app\unit_tests' 
        test_suite = unittest.TestLoader().discover(test_folder, pattern='test_*.py')

        xmlrunner.XMLTestRunner(output='test-reports').run(test_suite)
        convert_xml_to_html()
        
    finally:
        all_test_teardown()
        print('All tests complete')
    
if __name__ == '__main__':
    run_unit_tests()