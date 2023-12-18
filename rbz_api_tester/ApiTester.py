from typing import List
from logging import Logger
from rbz_api_tester.utils import read_json
from rbz_api_tester.Result import Result
from rbz_api_tester.TestStep import TestStep
from rbz_api_tester.TestSuite import TestSuite
from rbz_api_tester.TestSuiteResult import TestSuiteResult
from rbz_api_tester.ApiExecuter import ApiExecuter


class ReblazeApiTester:
    templates: str
    defaults: str
    planet: str
    branch:str
    api_key: str
    planet_url: str
    skipped_test_suites: int
    failed_test_suites: int
    passed_test_suites: int
    logger: Logger

    def __init__(
        self,
        templates_folder: str,
        defaults_folder: str,
        planet: str,
        branch: str,
        api_key: str,
        logger: Logger,
    ):
        self.templates = templates_folder
        self.defaults = defaults_folder
        self.planet = planet
        self.branch = branch
        self.api_key = api_key
        self.skipped_test_suites = 0
        self.failed_test_suites = 0
        self.passed_test_suites = 0
        self.logger = logger

    def _get_traffic_url(self):
        executer = ApiExecuter(api_key=self.api_key, planet=self.planet, headers=None, arguments=None, files=None, logger=self.logger)
        response = executer.get("/reblaze/api/v3/reblaze/tools/dns-information/")
        if response.status_code != 200 or response.reason != "OK":
            return ""

        json = response.json()
        for dns_record in json["dns_records"]:
            if dns_record["type"] == 'A' and self.branch in str(dns_record["name"]):
                return str(dns_record["name"]).rstrip(".")
        
        return ""

    def execute(self, test_suite_file: str):
        ts = read_json(test_suite_file)
        test_suite = TestSuite.from_dict(ts)

        self.traffic_url = self._get_traffic_url()

        self.logger.info(f"Executing Test Suite: {test_suite.name}")

        test_suite_result = test_suite.execute(
            self.templates, self.defaults, self.planet, self.branch, self.api_key, self.traffic_url, self.logger
        )

        if test_suite_result.result == Result.Passed:
            self.logger.info(f"Test Suite: {test_suite.name} Passed")
            self.passed_test_suites += 1
        elif test_suite_result.result == Result.Skipped:
            self.logger.warning(f"Test Suite: {test_suite.name} Skipped")
            self.skipped_test_suites += 1
        else:
            self.logger.error(f"Test Suite: {test_suite.name} Failed")
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

    def failure_report(self, results: List[TestSuiteResult]):
        errors = "\n"
        for result in results:
            if result.result == Result.Failed:
                errors += result.error_message + "\n\n"
        self.logger.error(errors)
