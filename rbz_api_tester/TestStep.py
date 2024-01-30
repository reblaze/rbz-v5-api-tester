import requests
import os
import json

from typing import List
from typing import Any
from pathlib import Path
from dataclasses import dataclass
from collections import OrderedDict

from rbz_api_tester.Param import Param
from rbz_api_tester.Payload import Payload
from rbz_api_tester.Expected import Expected
from rbz_api_tester.ApiResponse import ApiResponse
from rbz_api_tester.Result import Result
from rbz_api_tester.TestStepResult import TestStepResult
from rbz_api_tester.Executers.ApiExecuter import ApiExecuter
from rbz_api_tester.Executers.PythonExecuter import PythonExecuter
from rbz_api_tester.Executers.KubernetesExecuter import KubernetesExecuter
from rbz_api_tester.API import API
from rbz_api_tester.Time import convert_time_macros
from rbz_api_tester.CommonParameters import CommonParameters


@dataclass
class TestStep:
    step: int
    id: int
    name: str
    skip: bool
    debug_level: str
    debug_str: str
    generate_id: bool
    api: API
    method: str
    payload: Payload
    headers: List[Param]
    arguments: List[Param]
    files: List[Param]
    expected: Expected
    type: str
    code: List[str]

    def __init__(
        self,
        name: str,
        skip: bool,
        step: int = 0,
        id: str = None,
        debug_level: str = None,
        debug_str: str = None,
        generate_id: bool = False,
        api: API = None,
        method: str = None,
        payload: Payload = None,
        headers: List[Param] = None,
        arguments: List[Param] = None,
        files: List[Param] = None,
        expected: Expected = None,
        type: str = None,
        code: List[str] = None,
    ):
        self.id = id
        self.step = step
        self.name = name
        self.skip = skip
        self.debug_level = debug_level
        self.debug_str = debug_str
        self.generate_id = generate_id
        self.api = api
        self.method = method
        self.payload = payload
        self.headers = headers
        self.arguments = arguments
        self.files = files
        self.expected = expected
        self.type = type
        self.code = code

    @staticmethod
    def from_dict(obj: Any) -> "TestStep":
        _id = None
        _debug_level = None
        _debug_str = None
        _generate_id = None
        _api = None
        _payload = None
        _headers = None
        _arguments = None
        _files = None
        _expected = None
        _type = None
        _code = None

        if obj.get("Step") is not None:
            _step = int(obj.get("Step"))
        else:
            _step = 0
        if obj.get("ID") is not None:
            _id = obj.get("ID")
        _name = str(obj.get("Name"))
        _skip = bool(obj.get("Skip"))
        if obj.get("Debug") is not None:
            _debug_level = str(obj.get("Debug")["Level"])
            _debug_str = str(obj.get("Debug")["Message"])
        if obj.get("GenerateID") is not None:
            _generate_id = bool(obj.get("GenerateID"))
        if obj.get("API") is not None:
            _api = API.from_dict(obj.get("API"))
        _method = None
        if obj.get("Method") is not None:
            _method = str(obj.get("Method"))
        if obj.get("Payload") is not None:
            _payload = Payload.from_dict(obj.get("Payload"))
        if obj.get("Headers") is not None:
            _headers = [Param.from_dict(h) for h in obj.get("Headers")]
        if obj.get("Arguments") is not None:
            _arguments = [Param.from_dict(a) for a in obj.get("Arguments")]
        if obj.get("Files") is not None:
            _files = [Param.from_dict(f) for f in obj.get("Files")]
        if obj.get("Expected") is not None:
            _expected = Expected.from_dict(obj.get("Expected"))
        if obj.get("Type") is not None:
            _type = obj.get("Type")
        if obj.get("Code") is not None:
            _code = obj.get("Code", [])

        return TestStep(
            step=_step,
            id=_id,
            name=_name,
            skip=_skip,
            debug_level=_debug_level,
            debug_str=_debug_str,
            generate_id=_generate_id,
            api=_api,
            method=_method,
            payload=_payload,
            headers=_headers,
            arguments=_arguments,
            files=_files,
            expected=_expected,
            type=_type,
            code=_code,
        )

    def to_dict(self) -> dict:
        _id = None
        _debug = None
        _generate_id = None
        _api = None
        _method = None
        _payload = None
        _headers = None
        _arguments = None
        _files = None
        _expected = None
        _type = None
        _code = None

        result = OrderedDict(
            {
                "Name": self.name,
                "Skip": self.skip,
            }
        )

        if self.id is not None:
            result["ID"] = self.id
        if self.debug_level is not None and self.debug_str is not None:
            debug = {"Level": self.debug_level, "Message": self.debug_str}
            result["Debug"] = debug
        if self.generate_id is not None:
            result["GenerateID"] = self.generate_id
        if self.api is not None:
            result["API"] = self.api.to_dict()
        if self.method is not None:
            result["Method"] = self.method
        if self.headers is not None:
            result["Headers"] = [header.to_dict() for header in self.headers]
        if self.arguments is not None:
            result["Arguments"] = [argument.to_dict() for argument in self.arguments]
        if self.files is not None:
            result["Files"] = [file.to_dict() for file in self.files]
        if self.payload is not None:
            result["Payload"] = self.payload.to_dict()
        if self.expected is not None:
            result["Expected"] = self.expected.to_dict()
        if self.type is not None:
            result["Type"] = self.type
        if self.code is not None:
            result["Code"] = [line for line in self.code]

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

    def _execute_k8s(self) -> TestStepResult:
        result = TestStepResult()

        executer = KubernetesExecuter(
            params=self.arguments,
        )

        out, result.error_message = executer.execute()
        if len(result.error_message) == 0:
            result.result = Result.Passed
        else:
            result.result = Result.Failed
        return result

    def _execute_python(self) -> TestStepResult:
        result = TestStepResult()

        executer = PythonExecuter()

        res, out, result.error_message = executer.execute(self.code)
        if res == 0:
            result.result = Result.Passed
        else:
            result.result = Result.Failed
        return result

    def _execute_request(self) -> TestStepResult:
        result = TestStepResult()

        if self.arguments is not None:
            for arg in self.arguments:
                arg.value = convert_time_macros(arg.value)

        executer = ApiExecuter(
            generate_id=self.generate_id,
            headers=self.headers,
            arguments=self.arguments,
            files=self.files,
            api=self.api,
            method=self.method,
            payload=self.payload,
        )
        res = False
        msg = ""
        try:
            id, response = executer.execute()
            api_response: ApiResponse = ApiResponse()
            res, msg = api_response.validate(
                response=response, expected=self.expected, id=id, api=self.api
            )
        except requests.exceptions.RequestException as e:
            CommonParameters.logger.error(f"\t\tStep: {self.step} - Request error: {e}")
            msg = f"Request error: {e}\n"

        if not res:
            CommonParameters.logger.debug(
                f"Step: {self.step} - {self.name} ----->>>>>{msg}"
            )
        if res:
            result.result = Result.Passed
        else:
            result.result = Result.Failed
            result.error_message = f"Step: {self.step} - {self.name} ----->>>>>{msg}"

        return result

    def execute(self) -> TestStepResult:
        self.show_debug()
        CommonParameters.logger.debug(f"\t\tExecuting step: {self.step} - {self.name}")
        result = TestStepResult()

        if self.skip:
            result.result = Result.Skipped
            result.error_message = f"{self.step} - {self.name} ----->>>>> Skipping Test Step - Skip marked as true\n"
            return result

        if self.type == "python":
            test_step_result = self._execute_python()
        elif self.type == "kubernetes":
            test_step_result = self._execute_k8s()
        elif self.type == "request" or self.type is None:
            try:
                test_step_result = self._execute_request()
            except requests.exceptions.RequestException as e:
                CommonParameters.logger.error(
                    f"\t\tStep: {self.step} - Request error: {e}"
                )
                return (
                    False,
                    f"Step: {self.step} - {self.name} ----->>>>> Request error: {e}\n",
                )

        else:
            raise Exception(
                f"Unsupported type: {self.type}, supported values are: kubernetes, request or python"
            )

        return test_step_result
