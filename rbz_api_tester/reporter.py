from rbz_api_tester.CommonParameters import CommonParameters
from rbz_api_tester.Result import Result
from rbz_api_tester.TestSuiteResult import TestSuiteResult

class Reporter:
    def __init__(
        self,
        *,
        tester,
        num_of_test_suites,
        results: list[TestSuiteResult],
    ) -> None:
        self.tester = tester
        self.results = results
        self.num_of_test_suites = num_of_test_suites

    def report_console(self):
        logger = CommonParameters.logger
        tester = self.tester
        logger.info(
            f"---------------------------------  Summary --------------------------------"
        )
        logger.info(f"Total Test Suites: {self.num_of_test_suites}")
        logger.info(f"Passed Test Suites: {tester.passed_test_suites}")
        logger.info(f"Failed Test Suites: {tester.failed_test_suites}")
        logger.info(
            f"Skipped Test Suites: {tester.skipped_test_suites}"
        )
        logger.info(
            f"--------------------------- details on failures ---------------------------"
        )
        self.failure_report()
        logger.info(
            f"---------------------------------------------------------------------------"
        )

    def report_rich(self):
        pass

    def report_markdown(self):
        pass

    def failure_report(self):
        errors = "\n"
        for result in self.results:
            if result.result == Result.Failed:
                errors += result.error_message + "\n\n"
        CommonParameters.logger.error(errors)