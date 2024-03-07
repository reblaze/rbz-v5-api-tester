from typing import List
from rbz_api_tester.utils import read_json
from rbz_api_tester.Result import Result
from rbz_api_tester.TestStep import TestStep
from rbz_api_tester.TestSuite import TestSuite
from rbz_api_tester.TestSuiteResult import TestSuiteResult
from rbz_api_tester.Executers.ApiExecuter import ApiExecuter
from rbz_api_tester.CommonParameters import CommonParameters


class Tester:
    skipped_test_suites: int
    failed_test_suites: int
    passed_test_suites: int

    def __init__(self):
        self.skipped_test_suites = 0
        self.failed_test_suites = 0
        self.passed_test_suites = 0

    def execute(self, test_suite_file: str):
        ts = read_json(test_suite_file)
        test_suite = TestSuite.from_dict(ts)
        CommonParameters.logger.info(f"Executing Test Suite: {test_suite.name}")

        test_suite_result = test_suite.execute()

        if test_suite_result.result == Result.Passed:
            CommonParameters.logger.info(f"Test Suite: {test_suite.name} Passed")
            self.passed_test_suites += 1
        elif test_suite_result.result == Result.Skipped:
            CommonParameters.logger.warning(f"Test Suite: {test_suite.name} Skipped")
            self.skipped_test_suites += 1
        else:
            CommonParameters.logger.error(f"Test Suite: {test_suite.name} Failed")
            test_suite_result.error_message = (
                f"Test Suit File: {test_suite_file}\n" + test_suite_result.error_message
            )
            self.failed_test_suites += 1

        return test_suite_result

    def get_special_ids(self, test_suite_file: str):
        results = set()
        ts = read_json(test_suite_file)
        test_suite = TestSuite.from_dict(ts)
        for test in test_suite.tests:
            for step in test.steps:
                if step.payload is not None:
                    for param in step.payload.params:
                        if param.key == "id":
                            val = str(param.value.strip('"'))
                            if not val.startswith("api_tester_") and not val.startswith(
                                "__"
                            ):
                                results.add(val)
        return results
