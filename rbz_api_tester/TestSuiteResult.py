from typing import List
from rbz_api_tester.TestResult import TestResult
from rbz_api_tester.Result import Result


class TestSuiteResult:
    result: Result
    passed_tests: int
    skipped_tests: int
    failed_tests: int
    total_tests: int
    error_message: str
    items: List[TestResult]

    def __init__(self):
        self.passed_tests = 0
        self.skipped_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
        self.items = []
        self.error_message = ""
        self.result = Result.NotPerformed
