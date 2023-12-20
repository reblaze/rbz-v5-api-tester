from typing import List
from typing import Any
from dataclasses import dataclass
from logging import Logger
from rbz_api_tester.Result import Result

from rbz_api_tester.TestStep import TestStep
from rbz_api_tester.TestResult import TestResult


@dataclass
class Test:
    name: str
    skip: bool
    debug_level: str
    debug_str: str
    steps: List[TestStep]

    @staticmethod
    def from_dict(obj: Any) -> "Test":
        _name = str(obj.get("Name"))
        _skip = bool(obj.get("Skip"))
        _debug_level = None
        _debug_str = None
        if obj.get("Debug") is not None:
            _debug_level = str(obj.get("Debug")["Level"])
            _debug_str = str(obj.get("Debug")["Message"])
        _steps = [TestStep.from_dict(y) for y in obj.get("Steps")]
        return Test(_name, _skip, _debug_level, _debug_str, _steps)

    def to_dict(self) -> dict:
        debug = None
        if self.debug_level is not None and self.debug_str is not None:
            debug = {"Level": self.debug_level, "Message": self.debug_str}

        return {
            "Name": self.name,
            "Skip": self.skip,
            "Debug": debug,
            "Steps": [test_step.to_dict() for test_step in self.steps],
        }

    def show_debug(self, logger: Logger):
        if self.debug_level is not None and self.debug_str is not None:
            if self.debug_level == "info":
                logger.info(f">>>>> Debug from: {self.name}")
                logger.info(f"      {self.debug_str}")
            elif self.debug_level == "warning":
                logger.warning(f">>>>> Debug from: {self.name}")
                logger.warning(f"      {self.debug_str}")
            elif self.debug_level == "error":
                logger.error(f">>>>> Debug from: {self.name}")
                logger.error(f"      {self.debug_str}")
            elif self.debug_level == "debug":
                logger.debug(f">>>>> Debug from: {self.name}")
                logger.debug(f"      {self.debug_str}")

    def execute(
        self,
        shared_steps: {},
        templates: str,
        defaults: str,
        planet: str,
        branch: str,
        api_key: str,
        email: str,
        traffic_url: str,
        logger: Logger,
    ):
        self.show_debug(logger)
        logger.debug(f"\tStarting to execute test: {self.name}")
        result = TestResult()

        if self.skip:
            result.result = Result.Skipped
            result.error_message = f"{self.name}\nSkipping Test - Skip marked as true"
            return result

        result.total_steps = len(self.steps)
        i = 1
        for step in self.steps:
            if step.id is not None:
                skip = step.skip
                step = shared_steps[step.id]
                step.skip = skip

            step.step = i
            if step.python:
                test_step_result = step.execute_python(
                    planet, branch, api_key, email, traffic_url, logger
                )
            else:
                test_step_result = step.execute(
                    templates,
                    defaults,
                    planet,
                    branch,
                    api_key,
                    email,
                    traffic_url,
                    logger,
                )

            result.items.append(test_step_result)

            if test_step_result.result == Result.Passed:
                logger.debug(f"\t\tStep: {step.step} - {step.name} Passed")
                result.passed_steps += 1
            elif test_step_result.result == Result.Skipped:
                logger.warning(f"\t\tStep: {step.step} - {step.name} Skipped")
                result.skipped_steps += 1
            else:
                logger.error(f"\t\tStep: {step.step} - {step.name} Failed")
                result.error_message = f"{self.name} ----->>>>> Failed in Step: {step.step}\n\t\t{test_step_result.error_message}"
                result.failed_steps += 1
                break

            i += 1

        logger.debug(
            f"\t---------------------------------------------------------------------------"
        )
        logger.debug(f"\tDone executing test: {self.name}")
        logger.debug(f"\tTotal Steps: {result.total_steps}")
        logger.debug(f"\tPassed Steps: {result.passed_steps}")
        logger.debug(f"\tFailed Steps: {result.failed_steps}")
        logger.debug(f"\tSkipped Steps: {result.skipped_steps}")
        logger.debug(
            f"\t---------------------------------------------------------------------------"
        )

        if result.failed_steps == 0:
            result.result = Result.Passed
        else:
            result.result = Result.Failed

        return result
