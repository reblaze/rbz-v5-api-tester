from typing import List
from typing import Any
from dataclasses import dataclass
from collections import OrderedDict

from rbz_api_tester.Test import Test
from rbz_api_tester.TestResult import TestResult
from rbz_api_tester.TestSuiteResult import TestSuiteResult
from rbz_api_tester.Result import Result
from rbz_api_tester.CommonParameters import CommonParameters


@dataclass
class TestSuite:
    name: str
    skip: bool
    debug_level: str
    debug_str: str
    tests: List[Test]

    def __init__(
        self,
        name: str,
        skip: bool,
        debug_level: str = None,
        debug_str: str = None,
        tests: List[Test] = None,
    ):
        self.name = name
        self.skip = skip
        self.debug_level = debug_level
        self.debug_str = debug_str
        if tests is None:
            self.tests = list()
        else:
            self.tests = tests

    @staticmethod
    def from_dict(obj: Any) -> "TestSuite":
        _name = str(obj.get("Name"))
        _skip = bool(obj.get("Skip"))
        _debug_level = None
        _debug_str = None
        if obj.get("Debug") is not None:
            _debug_level = str(obj.get("Debug")["Level"])
            _debug_str = str(obj.get("Debug")["Message"])
        _tests = [Test.from_dict(y) for y in obj.get("Tests")]
        return TestSuite(_name, _skip, _debug_level, _debug_str, _tests)

    def to_dict(self) -> dict:
        debug = None
        if self.debug_level is not None and self.debug_str is not None:
            debug = {"Level": self.debug_level, "Message": self.debug_str}

        result = OrderedDict(
            {
            "Name": self.name,
            "Skip": self.skip,
            "Tests": [test.to_dict() for test in self.tests],
        }
        )

        if debug is not None:
            result["Debug"] = debug

        return result

    def show_debug(self):
        if self.debug_level is not None and self.debug_str is not None:
            if self.debug_level == "info":
                CommonParameters.logger.info(f">>>>> Debug from: {self.name}")
                CommonParameters.logger.info(f"      {self.debug_str}")
            elif self.debug_level == "warning":
                CommonParameters.logger.warning(f">>>>> Debug from: {self.name}")
                CommonParameters.logger.warning(f"      {self.debug_str}")
            elif self.debug_level == "error":
                CommonParameters.logger.error(f">>>>> Debug from: {self.name}")
                CommonParameters.logger.error(f"      {self.debug_str}")
            elif self.debug_level == "debug":
                CommonParameters.logger.debug(f">>>>> Debug from: {self.name}")
                CommonParameters.logger.debug(f"      {self.debug_str}")

    def execute(self):
        self.show_debug()
        CommonParameters.logger.debug(f"Starting to execute test suite: {self.name}")
        result = TestSuiteResult()

        if self.skip:
            result.result = Result.Skipped
            result.error_message = (
                f"{self.name}\nSkipping Test Suite - Skip marked as true"
            )
            return result

        result.total_tests = len(self.tests)
        result.error_message = f"Test Suite Name: {self.name}\n"
        for test in self.tests:
            test_result = test.execute()
            result.items.append(test_result)

            if test_result.result == Result.Passed:
                CommonParameters.logger.debug(f"\tTest: {test.name} Passed")
                result.passed_tests += 1
            elif test_result.result == Result.Skipped:
                CommonParameters.logger.debug(f"\tTest: {test.name} Skipped")
                result.skipped_tests += 1
            else:
                CommonParameters.logger.debug(f"\tTest: {test.name} Failed")
                result.error_message += (
                    f"\tFailure in Test: {test_result.error_message}"
                )
                result.failed_tests += 1

        CommonParameters.logger.debug(
            f"---------------------------------------------------------------------------"
        )
        CommonParameters.logger.debug(f"Done executing test suite: {self.name}")
        CommonParameters.logger.debug(f"Total Tests: {result.total_tests}")
        CommonParameters.logger.debug(f"Passed Tests: {result.passed_tests}")
        CommonParameters.logger.debug(f"Failed Tests: {result.failed_tests}")
        CommonParameters.logger.debug(f"Skipped Tests: {result.skipped_tests}")
        CommonParameters.logger.debug(
            f"---------------------------------------------------------------------------"
        )

        if result.failed_tests == 0:
            result.result = Result.Passed
        else:
            result.result = Result.Failed

        return result
