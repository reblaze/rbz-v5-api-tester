from typing import List

from rbz_api_tester.Result import Result
from rbz_api_tester.TestStepResult import TestStepResult


class TestResult:
    result: Result
    passed_steps: int
    skipped_steps: int
    failed_steps: int
    total_steps: int
    error_message: str
    items: List[TestStepResult]

    def __init__(self):
        self.passed_steps = 0
        self.skipped_steps = 0
        self.failed_steps = 0
        self.total_steps = 0
        self.items = []
        self.error_message = ""
        self.result = Result.NotPerformed
