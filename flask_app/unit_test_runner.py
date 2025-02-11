import unittest
import xmlrunner
import psycopg2 as pg
from dotenv import load_dotenv
load_dotenv(override=True)
import os
from dataclasses import dataclass
from datetime import datetime        
from jinja2 import Environment, FileSystemLoader

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

def parse_value(whole_str, label):
    start = whole_str.find(f'{label}=') + len(f'{label}="')
    end = whole_str.find('"', start)
    return whole_str[start:end]

# <failure type="AssertionError" message="2 != 1"><![CDATA[Traceback (most recent call last):
#   File "C:\Users\mattb\source\repos\mattburke1999\KeyboardGames\flask_app\unit_tests\test_auth.py", line 12, in test_sample2
#     self.assertEqual(2, 1)
# AssertionError: 2 != 1
# ]]></failure>
@dataclass
class TestFailure:
    type: str
    message: str
    traceback: str
    
    def __init__(self, failure: str):
        self.type = parse_value(failure, 'type')
        self.message = parse_value(failure, 'message')
        traceback_start = failure.find('<![CDATA[') + len('<![CDATA[')
        traceback_end = failure.find(']]>', traceback_start)
        self.traceback = failure[traceback_start:traceback_end].replace('\t', '')
# <testcase classname="test_auth.TestAuth" name="test_sample" time="0.001" timestamp="2025-02-10T17:50:46" file="flask_app\unit_tests\test_auth.py" line="8"/>
# <testcase classname="test_auth.TestAuth" name="test_sample2" time="0.001" timestamp="2025-02-10T17:50:46" file="flask_app\unit_tests\test_auth.py" line="11">
#     <failure type="AssertionError" message="2 != 1"><![CDATA[Traceback (most recent call last):
#         File "C:\Users\mattb\source\repos\mattburke1999\KeyboardGames\flask_app\unit_tests\test_auth.py", line 12, in test_sample2
#         self.assertEqual(2, 1)
#         AssertionError: 2 != 1
#         ]]>
#     </failure>
# </testcase>
@dataclass
class TestCase:
    name: str
    time: float
    timestamp: str
    file: str
    line_no: int
    failure: TestFailure | None
    
    def __init__(self, test_case: str):
        if '<failure' in test_case:
            failure_start = test_case.find('<failure')
            failure_end = test_case.find('</failure>') + len('</failure>')
            self.failure = TestFailure(test_case[failure_start:failure_end])
        else:
            self.failure = None
        self.name = parse_value(test_case, 'name')
        self.time = float(parse_value(test_case, 'time'))
        # we may convert to datetime and reformat later
        self.timestamp = parse_value(test_case, 'timestamp')
        self.file = parse_value(test_case, 'file')
        self.line_no = int(parse_value(test_case, 'line'))

def find_test_cases(test_suite: str):
    test_cases = []
    while '<testcase' in test_suite:
        test_case_start = test_suite.find('\n') + 1
        test_case_end = test_suite.find('\n', test_case_start)
        last_2_chars = test_suite[test_case_end - 2:test_case_end]
        test_case = None
        if last_2_chars == '/>':
            test_case_end = test_suite.find('/>', test_case_start) + len('/>')
            test_case = test_suite[test_case_start:test_case_end]
        else:
            test_case_end = test_suite.find('</testcase>') + len('</testcase>')
            test_case = test_suite[test_case_start:test_case_end]
        
        test_cases.append(TestCase(test_case))
        test_suite = test_suite[test_case_end:]
    return test_cases

# <testsuite name="test_auth.TestAuth-20250210175046" tests="2" file="test_auth.py" time="0.002" timestamp="2025-02-10T17:50:46" failures="1" errors="0" skipped="0">
# 	<testcase classname="test_auth.TestAuth" name="test_sample" time="0.001" timestamp="2025-02-10T17:50:46" file="flask_app\unit_tests\test_auth.py" line="8"/>
# 	<testcase classname="test_auth.TestAuth" name="test_sample2" time="0.001" timestamp="2025-02-10T17:50:46" file="flask_app\unit_tests\test_auth.py" line="11">
@dataclass
class TestSuite:
    test_cases: list[TestCase]
    name: str
    num_tests: int
    file: str
    time: float
    timestamp: str
    failures: int
    errors: int
    skipped: int
    
    def __init__(self, xml_test_report: str):
        self.name = parse_value(xml_test_report, 'name')
        self.num_tests = int(parse_value(xml_test_report, 'tests'))
        self.file = parse_value(xml_test_report, 'file')
        self.time = float(parse_value(xml_test_report, 'time'))
        self.timestamp = parse_value(xml_test_report, 'timestamp')
        self.failures = int(parse_value(xml_test_report, 'failures'))
        self.errors = int(parse_value(xml_test_report, 'errors'))
        self.skipped = int(parse_value(xml_test_report, 'skipped'))
        test_suite_start = xml_test_report.find('<testsuite')
        test_suite_end = xml_test_report.find('</testsuite>') + len('</testsuite>')
        test_suite = xml_test_report[test_suite_start:test_suite_end]
        self.test_cases = find_test_cases(test_suite)

test_report_html_dir = 'test-reports-html'
def render_test_report(test_suites: list, current_date: str) -> str:
    # Load the Jinja2 environment and specify the folder containing the template
    env = Environment(loader=FileSystemLoader(test_report_html_dir))  # Adjust folder if needed
    template = env.get_template('test-report-template.html')  # Load the template file

    # Render the template with test_suites data
    return template.render(test_suites=test_suites, current_date=current_date)

test_report_dir = 'test-reports'
def convert_xml_to_html():
    xml_files = os.listdir(test_report_dir)
    test_suites = []
    for file in xml_files:
        file_name = f'{test_report_dir}/{file}'
        with open(file_name, 'r') as xml_file:
            xml = xml_file.read()
            test_suites.append(TestSuite(xml))
    # will need to check if the timestamp is today, then convert to html, then delete all xml files
    current_date = datetime.now().strftime('%Y-%m-%d')
    html = render_test_report(test_suites, current_date)
    with open(f'{test_report_html_dir}\\reports\\test-report-{current_date}.html', 'w') as html_file:
        html_file.write(html)



            

all_test_setup()

try:
    test_folder = r'flask_app\unit_tests' 
    test_suite = unittest.TestLoader().discover(test_folder, pattern='test_*.py')

    xmlrunner.XMLTestRunner(output='test-reports').run(test_suite)
    # convert_xml_to_html()
       
finally:
    all_test_teardown()
    print('All tests complete')
    
if __name__ == '__main__':
    unittest.main()