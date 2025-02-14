
import os
from dataclasses import dataclass
from typing import Literal
from datetime import datetime
from datetime import timedelta

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

def parse_value(whole_str: str, label: str, type: type = str):
    start = whole_str.find(f'{label}=') + len(f'{label}="')
    end = whole_str.find('"', start)
    if type == datetime:
        return datetime.fromisoformat(whole_str[start:end])
    return type(whole_str[start:end])

@dataclass
class TestFailure:
    type: str
    message: str
    traceback: str
    id: int | None = None
    
    @classmethod
    def parse_failure(cls, failure: str, id = None):
        type = parse_value(failure, 'type')
        message = parse_value(failure, 'message')
        traceback_start = failure.find('<![CDATA[') + len('<![CDATA[')
        traceback_end = failure.find(']]>', traceback_start)
        traceback = failure[traceback_start:traceback_end].replace('\t', '')
        return cls(type, message, traceback, id)

@dataclass
class TestCase:
    name: str
    time: float
    file: str
    line_no: int
    passed: bool
    failure: TestFailure | None
    
    @classmethod
    def parse_test_case(cls, test_case: str):
        name = parse_value(test_case, 'name')
        time = parse_value(test_case, 'time', float)
        file = parse_value(test_case, 'file')
        line_no = parse_value(test_case, 'line', int)
        failure = None
        passed = True
        if '<failure' in test_case:
            failure_start = test_case.find('<failure')
            failure_end = test_case.find('</failure>') + len('</failure>')
            failure = TestFailure.parse_failure(test_case[failure_start:failure_end])
            passed = False
        return cls(name, time, file, line_no, passed, failure)
    
    @classmethod
    def from_db(cls, name: str, time: float, file: str, line_no: int, passed: bool, failures: dict | None):
        if failures:
            failures = TestFailure(**failures)
        return cls(name, time, file, line_no, passed, failures)
        

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
        
        test_cases.append(TestCase.parse_test_case(test_case))
        test_suite = test_suite[test_case_end:]
    return test_cases

@dataclass
class TestSuite:
    test_cases: list[TestCase]
    name: str
    type: Literal['unit', 'integration']
    num_tests: int
    file: str
    time: float
    timestamp: datetime
    failures: int
    errors: int
    skipped: int
    
    @classmethod
    def parse_test_report(cls, xml_test_report: str):
        name = parse_value(xml_test_report, 'name')
        type = 'unit' if r'flask_app\unit_tests' in xml_test_report else 'integration'
        num_tests = parse_value(xml_test_report, 'tests', int)
        file = parse_value(xml_test_report, 'file')
        time = parse_value(xml_test_report, 'time', float)
        timestamp = parse_value(xml_test_report, 'timestamp', datetime) + timedelta(days=-1)
        failures = parse_value(xml_test_report, 'failures', int)
        errors = parse_value(xml_test_report, 'errors', int)
        skipped = parse_value(xml_test_report, 'skipped', int)
        test_suite_start = xml_test_report.find('<testsuite')
        test_suite_end = xml_test_report.find('</testsuite>') + len('</testsuite>')
        test_suite = xml_test_report[test_suite_start:test_suite_end]
        test_cases = find_test_cases(test_suite)
        return cls(test_cases, name, type, num_tests, file, time, timestamp, failures, errors, skipped)
    
    @classmethod
    def from_db(cls, name: str, type: Literal['unit', 'integration'], num_tests: int, file: str, time: float, timestamp: datetime, failures: int, errors: int, skipped: int, test_cases: list[dict]):
        new_test_cases = []
        for test_case in test_cases:
            new_test_cases.append(TestCase.from_db(**test_case))
        return cls(new_test_cases, name, type, num_tests, file, time, timestamp, failures, errors, skipped)
            

def parse_xmls(test_report_dir = 'test-reports') -> list[TestSuite]:
    xml_files = os.listdir(test_report_dir)
    test_suites = []
    for file in xml_files:
        file_name = f'{test_report_dir}/{file}'
        with open(file_name, 'r') as xml_file:
            xml = xml_file.read()
            test_suites.append(TestSuite.parse_test_report(xml))
        # delete the xml file
        os.remove(file_name)
    return test_suites
    

