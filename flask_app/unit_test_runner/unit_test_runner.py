from flask import Flask
from flask import request
from flask import render_template
import unittest
import xmlrunner
import psycopg2 as pg
from dataclasses import asdict
from dotenv import load_dotenv
from datetime import datetime
load_dotenv(override=True)
import os
import sys
import traceback
from xml_parser import parse_xmls
from xml_parser import TestSuite
from xml_parser import TestCase
from xml_parser import TestFailure

sql_create = r'db_files\games_table.sql'

def connect_db():
    conn = pg.connect(os.getenv('DATABASE_URL'))
    return conn

def test_connect_db():
    conn = pg.connect(os.getenv('TEST_DATABASE_URL'))
    return conn

def all_test_setup(save_to_db: bool, test_report_dir: str):
    if save_to_db:
        if os.path.exists(test_report_dir):
            # remove previous test results
            for file in os.listdir(test_report_dir):
                os.remove(f'{test_report_dir}/{file}')
        print('Test report directory cleaned')
    sql_create_script = None
    with open(sql_create, 'r') as file:
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

def insert_test_failure(test_failure: TestFailure, test_case_id: int, conn: pg.extensions.connection):
    with conn.cursor() as cur:
        cur.execute('insert into unit_tests.failures (test_case_id, type, message, traceback) values (%s, %s, %s, %s);', 
            (test_case_id, test_failure.type, test_failure.message, test_failure.traceback))

def insert_test_case(test_case: TestCase, test_suite_id: int, conn: pg.extensions.connection):
    with conn.cursor() as cur:
        cur.execute('insert into unit_tests.test_case (test_suite_id, name, time, file, line_no, passed) values (%s, %s, %s, %s, %s, %s) returning id;', 
            (test_suite_id, test_case.name, test_case.time, test_case.file, test_case.line_no, test_case.passed))
        result = cur.fetchone()
        if not result:
            raise Exception('Failed to insert test case')
        test_case_id = result[0]
        if test_case.failure is not None:
            insert_test_failure(test_case.failure, test_case_id, conn)

def insert_test_suite(test_suite: TestSuite, conn: pg.extensions.connection):
    with conn.cursor() as cur:
        cur.execute('insert into unit_tests.test_suite (name, type, num_tests, file, time, timestamp, failures, errors, skipped) values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning id;', 
            (test_suite.name, test_suite.type, test_suite.num_tests, test_suite.file, test_suite.time, test_suite.timestamp, test_suite.failures, test_suite.errors, test_suite.skipped))
        result = cur.fetchone()
    if not result:
        raise Exception('Failed to insert test suite')
    test_suite_id = result[0]
    for test_case in test_suite.test_cases:
        insert_test_case(test_case, test_suite_id, conn)
    return

def insert_test_suites_into_db(test_suites: list[TestSuite]):
    # will need to check if the timestamp is today before inserting
    with connect_db() as conn:
        try:
            for test_suite in test_suites:
                insert_test_suite(test_suite, conn)
            conn.commit()
        except:
            traceback.print_exc()
            conn.rollback()
            # if database insert fails, we will write to a temporary json file for the time being
            
def run_tests(save_to_db=False):
    
    test_report_dir = 'test-reports'
    all_test_setup(save_to_db, test_report_dir)

    try:
        test_folder = 'flask_app' 
        test_suite = unittest.TestLoader().discover(test_folder, pattern='test_*.py')

        xmlrunner.XMLTestRunner(output=test_report_dir).run(test_suite)
        if save_to_db:
            print('saving results to db')
            test_suites = parse_xmls(test_report_dir)
            insert_test_suites_into_db(test_suites)
        
    finally:
        all_test_teardown()
        print('All tests complete')

### Minimal Flask app to display test results
app = Flask(__name__)

def render_error_page():
    return '''
        <html>
            <head>
                <title>Keyboard Games Test Results</title>
            </head>
            <body>
                <h1 style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">Error loading tests.</h1>
            </body>
        </html>                
    '''

def get_test_dates() -> list[datetime] | None:
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute('select distinct timestamp from unit_tests.test_suite order by timestamp desc;')
            results = cur.fetchall()
    return [result[0] for result in results] if results else None
        
def get_test_suites(timestamp):
    print(timestamp)
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
            '''
                select name, type, num_tests, file, time, timestamp, failures, errors, skipped, test_cases
                from unit_tests.test_view 
                where timestamp::date = %s;
            ''', (timestamp,))
            results = cur.fetchall()
    return [TestSuite.from_db(*result) for result in results] if results else None

def get_all_failures_from_test_suites(test_suites: list[TestSuite]):
    failures = {}
    for test_suite in test_suites:
        for test_case in test_suite.test_cases:
            if test_case.failure:
                failure = asdict(test_case.failure)
                failure = {**failure, 'name': test_case.name, 'time': test_case.time, 'file': test_case.file}
                failures[failure.pop('id')] = failure
    return failures

@app.route('/')
def index():
    timestamp = request.args.get('timestamp', None)
    all_dates = get_test_dates()
    if not all_dates:
        return render_error_page()
    if not timestamp:
        timestamp = all_dates[0]
        # parse to just date from 2025-02-11 16:56:45
        timestamp = timestamp.strftime('%Y-%m-%d')
    all_dates = [date.strftime('%Y-%m-%d') for date in all_dates]
    test_suites = get_test_suites(timestamp)
    if not test_suites:
        return render_error_page()
    unit_test_suites = [test_suite for test_suite in test_suites if test_suite.type == 'unit']
    integration_test_suites = [test_suite for test_suite in test_suites if test_suite.type == 'integration']
    failures = get_all_failures_from_test_suites(test_suites)
    return render_template('test-report-template.html', 
        unit_test_suites=unit_test_suites, integration_test_suites=integration_test_suites, all_dates=all_dates, current_date=timestamp, failures=failures, len=len)

def start_app():
    app.run(debug=True)

if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '-view':
        start_app()
    else:
        save_to_db = True if args and args[0] == '-save' else False
        run_tests(save_to_db)