import requests
import os
import json
import uuid
import subprocess

from typing import List
from typing import Any
from pathlib import Path
from dataclasses import dataclass
from logging import Logger

from rbz_api_tester.utils import from_alias, from_api
from rbz_api_tester.Param import Param
from rbz_api_tester.Payload import Payload
from rbz_api_tester.Expected import Expected
from rbz_api_tester.Result import Result
from rbz_api_tester.TestStepResult import TestStepResult
from rbz_api_tester.ApiExecuter import ApiExecuter
from rbz_api_tester.API import API


@dataclass
class TestStep:
    step: int
    name: str
    skip: bool
    debug_level: str
    debug_str: str
    generate_id: bool
    traffic: bool
    api: API
    method: str
    payload: Payload
    headers: List[Param]
    expected: Expected
    python: bool
    code: List[str]
    
    @staticmethod
    def from_dict(obj: Any) -> "TestStep":
        if obj.get("Step") is not None:
            _step = int(obj.get("Step"))
        else:
            _step = 0
        _name = str(obj.get("Name"))
        _skip = bool(obj.get("Skip"))
        _debug_level = None
        _debug_str = None
        if obj.get("Debug") is not None:
            _debug_level = str(obj.get("Debug")["Level"])
            _debug_str = str(obj.get("Debug")["Message"])
        _generate_id = None
        if obj.get("GenerateID") is not None:
            _generate_id = bool(obj.get("GenerateID"))
        _traffic = False
        if obj.get("Traffic") is not None:
            _traffic = bool(obj.get("Traffic"))
        _api = None
        if obj.get("API") is not None:
            _api = API.from_dict(obj.get("API"))
        _method = None
        if obj.get("Method") is not None:
            _method = str(obj.get("Method"))
        _payload = None
        _headers = None
        _python = False
        _code = None
        if obj.get("Payload") is not None:
            _payload = Payload.from_dict(obj.get("Payload"))
        if obj.get("Headers") is not None:
            _headers = [Param.from_dict(y) for y in obj.get("Headers")]
        _expected = None
        if obj.get("Expected") is not None:
            _expected = Expected.from_dict(obj.get("Expected"))
        if obj.get("Python") is not None:
            _python = bool(obj.get("Python"))
        if obj.get("Code") is not None:
            _code = obj.get("Code", [])

        return TestStep(
            _step,
            _name,
            _skip,
            _debug_level,
            _debug_str,
            _generate_id,
            _traffic,
            _api,
            _method,
            _payload,
            _headers,
            _expected,
            _python,
            _code
        )

    def to_dict(self) -> dict:
        _debug = None
        _generate_id = None
        _traffic = None
        _api = None
        _method = None
        _payload = None
        _headers = None
        _expected = None
        _python = None
        _code = None

        if self.debug_level is not None and self.debug_str is not None:
            debug = {"Level": self.debug_level, "Message": self.debug_str}
        if self.generate_id is not None:
            _generate_id = self.generate_id
        if self.traffic is not None:
            _traffic = self.traffic
        if self.api is not None:
            _api = self.api.to_dict()
        if self.method is not None:
            _method = self.method
        if self.payload is not None:
            _payload = self.payload.to_dict()
        if self.headers is not None:
            _headers = [header.to_dict() for header in self.headers]
        if self.expected is not None:
            _expected = self.expected.to_dict()
        if self.python is not None:
            _python = self.python
        if self.code is not None:
            _code = [line for line in self.code]

        return {
            "Step": self.step,
            "Name": self.name,
            "Skip": self.skip,
            "Debug": _debug,
            "GenerateID": _generate_id,
            "Traffic": _traffic,
            "API": _api,
            "Method": _method,
            "Payload": _payload,
            "Headers": _headers,
            "Expected": _expected,
            "Python": _python,
            "Code": _code,
        }

    def show_debug(self):
        if self.debug_level is not None and self.debug_str is not None:
            if self.debug_level == "info":
                self.logger.info(f">>>>> Debug from: {self.name}")
                self.logger.info(f"      {self.debug_str}")
            elif self.debug_level == "warning":
                self.logger.warning(f">>>>> Debug from: {self.name}")
                self.logger.warning(f"      {self.debug_str}")
            elif self.debug_level == "error":
                self.logger.error(f">>>>> Debug from: {self.name}")
                self.logger.error(f"      {self.debug_str}")
            elif self.debug_level == "debug":
                self.logger.debug(f">>>>> Debug from: {self.name}")
                self.logger.debug(f"      {self.debug_str}")

    def _generate_uuid(self):
        dt = int((uuid.uuid1().time * 10000) & 0xFFFFFFFFFFFF)
        return "api_tester_" + str(uuid.UUID(f"{dt:032x}")).split("-")[4]

    def _get_payload(
        self, payload: Payload, id: str, templates_folder: str, defaults_folder: str
    ):
        template_file = os.path.join(Path(templates_folder).resolve(), payload.template)
        defaults_file = os.path.join(Path(defaults_folder).resolve(), payload.defaults)
        templates_contents = Path(template_file).read_text()

        if id is not None:
            templates_contents = templates_contents.replace("@@id@@", '"' + id + '"')
        
        for param in payload.params:
            key = "@@" + param.key + "@@"
            value = param.value
            templates_contents = templates_contents.replace(key, value)

        defaults_contents = Path(defaults_file).read_text()
        defaults = defaults_contents.split("\n")
        for default in defaults:
            touple = default.split("=")
            key = f"@@{touple[0]}@@"
            value = touple[1:]
            value1 = str("=".join(value))
            templates_contents = templates_contents.replace(key, value1)

        templates_contents = templates_contents.replace("@@branch@@", self.branch)
        templates_contents = templates_contents.replace("@@planet@@", self.planet)

        return json.loads(templates_contents)

    def _compare_expected_to_response(self, expected: Param, response: dict, id: str):
        types_with_no_quotes = (int, bool, float)
        key = expected.key
        expected_value = expected.value
        if type(expected.value) is str and id is not None:
            expected_value = str(expected_value).replace("@@id@@", id)
        value = response[key]
        if isinstance(value, types_with_no_quotes):
            return value == expected_value
        else:
            return str(value) == expected_value

    def _find_in_response(self, expected: List[Param], response: dict, id: str):
        search = len(expected)
        found = 0
        for element in response:
            found = 0
            for expected_result in expected:
                if self._compare_expected_to_response(expected_result, element, id):
                    found += 1
                    if search == found:
                        return True
        return False

    def _check_response_json_single(self, response_json, id: str):
        if self.expected.single_result is not None:
            for expected_result in self.expected.single_result:
                if not self._compare_expected_to_response(
                    expected_result, response_json, id
                ):
                    return (
                        False,
                        f"Step: {self.step} - {self.name} ----->>>>> Expected Key: {expected_result.key} to have Value: {expected_result.value} but response was: {response_json}\n",
                    )
            return True, ""
        else:
            return (
                False,
                f"Step: {self.step} - {self.name} ----->>>>> Failed because no 'SingleResults' criteria defined\n",
            )

    def _check_response_json_multiple(self, response_json, id: str):
        if self.expected.multiple_results is not None:
            for expected_result in self.expected.multiple_results:
                if not self._find_in_response(expected_result, response_json, id):
                    return (
                        False,
                        f"Step: {self.step} - {self.name} ----->>>>> Could not find: {expected_result.value} in response: {response_json}\n",
                    )
            return True, ""
        else:
            return (
                False,
                f"Step: {self.step} - {self.name} ----->>>>> Failed because no 'MultipleResults' criteria defined\n",
            )

    def _check_response_json(self, response, id: str):
        response_json = response.json()
        if self.expected.single:
            return self._check_response_json_single(response_json, id)
        else:
            return self._check_response_json_multiple(response_json, id)

    def _check_response(self, response, id, expected_text):
        if self.expected.code == response.status_code:
            if self.expected.type == "json":
                return self._check_response_json(response, id)
            elif self.expected.type == "content":
                if expected_text == str(response.content) or self.traffic:
                    return True, ""
                else:
                    return (
                        False,
                        f"Step: {self.step} - {self.name} ----->>>>> Expected Text: {expected_text} Actual Text: {str(response.content)}\n",
                    )
            else:
                return (
                    False,
                    f"Step: {self.step} - {self.name} ----->>>>> unknown Expected Type: {self.expected.type}\n",
                )
        else:
            return (
                False,
                f"Step: {self.step} - {self.name} ----->>>>> Expected Code: {self.expected.code} Actual Code: {response.status_code}\n",
            )

    def _set_id_and_params(
        self, templates_folder, defaults_folder, expected_text
    ):
        id = None
        final_api_url = self.api.get()
        if self.generate_id:
            id = self._generate_uuid()
            final_api_url = self.api.get().replace("@@id@@", id)
            if expected_text is not None:
                expected_text = expected_text.replace("@@id@@", id)

        final_api_url = final_api_url.replace("@@branch@@", self.branch)

        actual_payload = self._get_payload(
            self.payload, id, templates_folder, defaults_folder
        )

        return final_api_url, id, expected_text, actual_payload

    def _post_api(
        self, templates_folder: str, defaults_folder: str
    ):
        try:
            id = None
            expected_text = self.expected.text

            final_api_url, id, expected_text, payload = self._set_id_and_params(
                templates_folder, defaults_folder, expected_text
            )

            executer = ApiExecuter(api_key=self.api_key, planet=self.planet, headers=self.headers, logger=self.logger)
            response = executer.post(final_api_url, payload)
            res, msg = self._check_response(response, id, expected_text)
            if not res:
                self.logger.debug(msg)
            return res, msg
        except requests.exceptions.RequestException as e:
            self.logger.error(f"\t\tStep: {self.step} - Request error: {e}")
            return (
                False,
                f"Step: {self.step} - {self.name} ----->>>>> Request error: {e}\n",
            )

    def _put_api(
        self, templates_folder: str, defaults_folder: str
    ):
        try:
            id = None
            expected_text = self.expected.text

            final_api_url, id, expected_text, payload = self._set_id_and_params(
                templates_folder, defaults_folder, expected_text
            )

            executer = ApiExecuter(api_key=self.api_key, planet=self.planet, headers=self.headers, logger=self.logger)
            response = executer.put(final_api_url, payload)
            res, msg = self._check_response(response, id, expected_text)
            if not res:
                self.logger.debug(msg)
            return res, msg
        except requests.exceptions.RequestException as e:
            self.logger.error(f"\t\tStep: {self.step} - Request error: {e}")
            return (
                False,
                f"Step: {self.step} - {self.name} ----->>>>> Request error: {e}\n",
            )

    def _get_api(self):
        try:
            id = None
            expected_text = self.expected.text

            if self.generate_id:
                id = self._generate_uuid()
                expected_text = expected_text.replace("@@id@@", id)

            final_api = self.api.get().replace("@@branch@@", self.branch)

            executer = ApiExecuter(api_key=self.api_key, planet=self.planet, headers=self.headers, logger=self.logger)
            response = executer.get(final_api)

            res, msg = self._check_response(response, id, expected_text)
            if not res:
                self.logger.debug(msg)
            return res, msg
        except requests.exceptions.RequestException as e:
            self.logger.error(f"\t\tStep: {self.step} - Request error: {e}")
            return (
                False,
                f"Step: {self.step} - {self.name} ----->>>>> Request error: {e}\n",
            )

    def _delete_api(self):
        try:
            executer = ApiExecuter(api_key=self.api_key, planet=self.planet, headers=self.headers, logger=self.logger)
            final_api = self.api.get().replace("@@branch@@", self.branch)
            response = executer.delete(final_api)

            if response.status_code == 200 and response.json()["ok"]:
                return True, ""
            elif response.status_code == 204:
                return True, ""
            else:
                msg = f"Step: {self.step} - {self.name} ----->>>>> Expected Code: 200 or 204 Actual Code: {response.status_code}\n"
                self.logger.debug(msg)
                return (
                    False,
                    msg,
                )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"\t\tStep: {self.step} - Request error: {e}")
            return (
                False,
                f"Step: {self.step} - {self.name} ----->>>>> Request error: {e}\n",
            )

    def _send_traffic(self):
        try:
            expected_text = self.expected.text
            executer = ApiExecuter(api_key=self.api_key, planet=self.planet, headers=self.headers, logger=self.logger)
            response = executer.send(self.traffic_url)

            res, msg = self._check_response(response, id, expected_text)
            if not res:
                self.logger.debug(msg)
            return res, msg
        except requests.exceptions.RequestException as e:
            self.logger.error(f"\t\tStep: {self.step} - Request error: {e}")
            return (
                False,
                f"Step: {self.step} - {self.name} ----->>>>> Request error: {e}\n",
            )

    def execute_python(self, logger: Logger):
        self.logger = logger
        self.show_debug()
        self.logger.debug(f"\t\tExecuting step: {self.step} - {self.name}")
        code = "\n".join(self.code)
        self.logger.debug(f"\t\tPython Script:\n{code}")
        result = TestStepResult()

        if self.skip:
            result.result = Result.Skipped
            result.error_message = f"{self.step} - {self.name} ----->>>>> Skipping Test Step - Skip marked as true\n"
            return result

        process = subprocess.Popen(["python"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        stdout, stderr = process.communicate(input=code)
        if stdout != '':
            self.logger.debug(f"\t\tOutput:\n{stdout}")
        if stderr != '':
            self.logger.debug(f"\t\tError:\n{stderr}")
        result.error_message = stderr
        if process.returncode == 0:
            result.result = Result.Passed
        else:
            result.result = Result.Failed
        return result

    def execute(
            self, templates: str, defaults: str, planet: str, branch: str, api_key: str, traffic_url: str, logger: Logger
    ):
        self.api_key = api_key
        self.planet = planet
        self.branch = branch
        self.traffic_url = traffic_url
        self.logger = logger
        self.show_debug()
        self.logger.debug(f"\t\tExecuting step: {self.step} - {self.name}")
        result = TestStepResult()

        if self.skip:
            result.result = Result.Skipped
            result.error_message = f"{self.step} - {self.name} ----->>>>> Skipping Test Step - Skip marked as true\n"
            return result

        if self.traffic:
            res, result.error_message = self._send_traffic()
        elif self.method == "POST":
            res, result.error_message = self._post_api(templates, defaults)
        elif self.method == "PUT":
            res, result.error_message = self._put_api(templates, defaults)
        elif self.method == "GET":
            res, result.error_message = self._get_api()
        elif self.method == "DELETE":
            res, result.error_message = self._delete_api()

        if res:
            result.result = Result.Passed
        else:
            result.result = Result.Failed

        return result







