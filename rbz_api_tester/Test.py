from typing import List
from typing import Any
from dataclasses import dataclass
from collections import OrderedDict

from rbz_api_tester.Result import Result
from rbz_api_tester.TestStep import TestStep
from rbz_api_tester.TestResult import TestResult
from rbz_api_tester.utils import read_json
from rbz_api_tester.CommonParameters import CommonParameters


@dataclass
class Test:
    name: str
    skip: bool
    debug_level: str
    debug_str: str
    steps: List[TestStep]

    def __init__(
        self,
        name: str,
        skip: bool,
        debug_level: str = None,
        debug_str: str = None,
        steps: List[TestStep] = None,
    ):
        self.name = name
        self.skip = skip
        self.debug_level = debug_level
        self.debug_str = debug_str
        self.steps = steps

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
        return Test(
            name=_name,
            skip=_skip,
            debug_level=_debug_level,
            debug_str=_debug_str,
            steps=_steps,
        )

    def to_dict(self) -> dict:
        debug = None
        if self.debug_level is not None and self.debug_str is not None:
            debug = {"Level": self.debug_level, "Message": self.debug_str}

        result = OrderedDict(
            {
                "Name": self.name,
                "Skip": self.skip,
                "Steps": [test_step.to_dict() for test_step in self.steps],
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

    def load_shared_steps(self) -> {}:
        shared_steps = {}
        shared = read_json(CommonParameters.shared_steps)
        for step in shared:
            shared_steps[step["ID"]] = TestStep.from_dict(step["Step"])
        return shared_steps

    def execute(self):
        self.show_debug()
        CommonParameters.logger.debug(f"\tStarting to execute test: {self.name}")
        result = TestResult()

        if self.skip:
            result.result = Result.Skipped
            result.error_message = f"{self.name}\nSkipping Test - Skip marked as true"
            return result

        result.total_steps = len(self.steps)
        i = 1
        shared_steps = self.load_shared_steps()

        for step in self.steps:
            if step.id is not None:
                skip = step.skip
                step = shared_steps[step.id]
                step.skip = skip

            step.step = i
            test_step_result = step.execute()

            result.items.append(test_step_result)

            if test_step_result.result == Result.Passed:
                CommonParameters.logger.debug(
                    f"\t\tStep: {step.step} - {step.name} Passed"
                )
                result.passed_steps += 1
            elif test_step_result.result == Result.Skipped:
                CommonParameters.logger.warning(
                    f"\t\tStep: {step.step} - {step.name} Skipped"
                )
                result.skipped_steps += 1
            else:
                CommonParameters.logger.error(
                    f"\t\tStep: {step.step} - {step.name} Failed"
                )
                result.error_message = f"{self.name} ----->>>>> Failed in Step: {step.step}\n\t\t{test_step_result.error_message}"
                result.failed_steps += 1
                break

            i += 1

        CommonParameters.logger.debug(
            f"\t---------------------------------------------------------------------------"
        )
        CommonParameters.logger.debug(f"\tDone executing test: {self.name}")
        CommonParameters.logger.debug(f"\tTotal Steps: {result.total_steps}")
        CommonParameters.logger.debug(f"\tPassed Steps: {result.passed_steps}")
        CommonParameters.logger.debug(f"\tFailed Steps: {result.failed_steps}")
        CommonParameters.logger.debug(f"\tSkipped Steps: {result.skipped_steps}")
        CommonParameters.logger.debug(
            f"\t---------------------------------------------------------------------------"
        )

        if result.failed_steps == 0:
            result.result = Result.Passed
        else:
            result.result = Result.Failed

        return result
