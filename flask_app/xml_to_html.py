
import os
from dataclasses import dataclass
from datetime import datetime        
from jinja2 import Environment, FileSystemLoader

current_date = datetime.now().strftime('%Y-%m-%d')

def sample_xml():
    return r"""
Sample XML output:

<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="test_auth.TestAuth-20250210204249" tests="2" file="test_auth.py" time="0.004" timestamp="2025-02-10T20:42:49" failures="1" errors="0" skipped="0">
	<testcase classname="test_auth.TestAuth" name="test_sample" time="0.003" timestamp="2025-02-10T20:42:49" file="flask_app\unit_tests\test_auth.py" line="8"/>
	<testcase classname="test_auth.TestAuth" name="test_sample2" time="0.001" timestamp="2025-02-10T20:42:49" file="flask_app\unit_tests\test_auth.py" line="11">
		<failure type="AssertionError" message="2 != 1"><![CDATA[Traceback (most recent call last):
  File "C:\Users\mattb\KeyboardGame\flask_app\unit_tests\test_auth.py", line 12, in test_sample2
    self.assertEqual(2, 1)
AssertionError: 2 != 1
]]></failure>
	</testcase>
</testsuite>
"""

def parse_value(whole_str, label):
    start = whole_str.find(f'{label}=') + len(f'{label}="')
    end = whole_str.find('"', start)
    return whole_str[start:end]

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


def render_test_report(test_suites: list, test_report_html_dir: str) -> str:
    # Load the Jinja2 environment and specify the folder containing the template
    env = Environment(loader=FileSystemLoader(test_report_html_dir))  # Adjust folder if needed
    template = env.get_template('test-report-template.html')  # Load the template file
    # Render the template with test_suites data
    return template.render(test_suites=test_suites, current_date=current_date)


def convert_xml_to_html(test_report_dir = 'test-reports', test_report_html_dir = 'test-reports-html'):
    xml_files = os.listdir(test_report_dir)
    test_suites = []
    for file in xml_files:
        file_name = f'{test_report_dir}/{file}'
        with open(file_name, 'r') as xml_file:
            xml = xml_file.read()
            test_suites.append(TestSuite(xml))
        # delete the xml file
        os.remove(file_name)
    # will need to check if the timestamp is today, then convert to html, then delete all xml files
    html = render_test_report(test_suites, test_report_html_dir)
    with open(f'{test_report_html_dir}\\reports\\test-report-{current_date}.html', 'w') as html_file:
        html_file.write(html)
