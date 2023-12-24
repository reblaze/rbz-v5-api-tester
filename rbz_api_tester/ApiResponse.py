import requests
from typing import List

from rbz_api_tester.Expected import Expected
from rbz_api_tester.Param import Param
from rbz_api_tester.API import API
from rbz_api_tester.CommonParameters import CommonParameters


class ApiResponse:
    def _prepare_expected_headers(self):
        if self.expected.headers is not None:
            for h in self.expected.headers:
                if type(h.value) is str and self.id is not None:
                    self.expected.headers[h.key] = h.value.replace("@@id@@", self.id)

    def _prepare_expected_text(self):
        if self.expected.text is not None and self.id is not None:
            self.expected.text = self.expected.text.replace("@@id@@", self.id)

    def _prepare_single_result(self):
        for param in self.expected.single_result:
            if type(param.value) is str and self.id is not None:
                self.expected.single_result[param.key] = param.value.replace(
                    "@@id@@", self.id
                )

    def _prepare_multiple_results(self):
        index = 0
        for result in self.expected.multiple_results:
            for param in result:
                if type(param.value) is str and self.id is not None:
                    self.expected.multiple_results[index][
                        param.key
                    ] = param.value.replace("@@id@@", self.id)
            index = index + 1

    def _prepare_expected_results(self):
        if self.expected.single_result is not None:
            self._prepare_single_result()
        elif self.expected.multiple_results is not None:
            self._prepare_multiple_results()

    def _check_response_content(self) -> (bool, str):
        if (
            self.expected.text == str(self.response.content)
            or self.api.is_send_traffic()
        ):
            return True, ""
        else:
            return (
                False,
                f"Expected Text: {self.expected.text} Actual Text: {str(self.response.content)}\n",
            )

    def _compare_expected_to_response_jsonpath(
        self, expected: Param, response: dict
    ) -> bool:
        try:
            types_with_no_quotes = (int, bool, float)
            keys = expected.key.split("/")
            value = response
            for key in keys:
                if key == "*":
                    return any(element == expected.value for element in value)
                if key.isnumeric():
                    value = value[int(key)]
                else:
                    value = value[key]
            if isinstance(value, types_with_no_quotes):
                return value == expected.value
            else:
                return str(value) == expected.value
        except Exception as e:
            CommonParameters.logger.error(f"json path check failed due to: {repr(e)}")
            return False

    def _check_response_jsonpath(self) -> (bool, str):
        response_json = self.response.json()
        for expected_result in self.expected.single_result:
            if not self._compare_expected_to_response_jsonpath(
                expected_result, response_json
            ):
                return (
                    False,
                    f"Expected Key: {expected_result.key} to have Value: {expected_result.value} but response was: {response_json}\n",
                )
        return True, ""

    def _find_in_response(self, expected: List[Param], response: dict) -> bool:
        search = len(expected)
        found = 0
        for element in response:
            found = 0
            for expected_result in expected:
                if self._compare_expected_to_response(expected_result, element):
                    found += 1
                    if search == found:
                        return True
        return False

    def _check_response_json_multiple(self) -> (bool, str):
        response_json = self.response.json()
        if self.expected.multiple_results is not None:
            for expected_result in self.expected.multiple_results:
                if not self._find_in_response(expected_result, response_json):
                    return (
                        False,
                        f"Could not find: {expected_result.value} in response: {response_json}\n",
                    )
            return True, ""
        else:
            return (
                False,
                f"Failed because no 'MultipleResults' criteria defined\n",
            )

    def _compare_expected_to_response(self, expected: Param, response: dict) -> bool:
        types_with_no_quotes = (int, bool, float)
        key = expected.key
        value = response[key]
        if isinstance(value, types_with_no_quotes):
            return value == expected.value
        else:
            return str(value) == expected.value

    def _check_response_json_single(self) -> (bool, str):
        response_json = self.response.json()
        if self.expected.single_result is not None:
            for expected_result in self.expected.single_result:
                if not self._compare_expected_to_response(
                    expected_result, response_json
                ):
                    return (
                        False,
                        f"Expected Key: {expected_result.key} to have Value: {expected_result.value} but response was: {response_json}\n",
                    )
            return True, ""
        else:
            return (
                False,
                f"Failed because no 'SingleResults' criteria defined\n",
            )

    def _check_response_json(self) -> (bool, str):
        if self.expected.single:
            return self._check_response_json_single()
        else:
            return self._check_response_json_multiple()

    def _check_response_headers(self) -> (bool, str):
        expected = ""
        actual = ""
        if self.expected.headers is not None:
            for h in self.expected.headers:
                if self.response.headers[h.key] is None:
                    expected, actual = self._format_headers_message()
                    return (
                        False,
                        f"{expected}\n{actual}\n",
                    )
                elif self.response.headers[h.key] != h.value:
                    expected, actual = self._format_headers_message()
                    return (
                        False,
                        f"{expected}\n{actual}\n",
                    )
        return (True, "")

    def _format_headers_message(self) -> (str, str):
        expected_headers = "Expected Headers:"
        for h in self.expected.headers:
            expected_headers = f"{expected_headers}\nKey: {h.key}, Value:{h.value}"
        actual_headers = "Actual Headers:"
        for header, value in self.response.headers.items():
            actual_headers = f"{actual_headers}\nKey: {header}, Value:{value}"
        return (expected_headers, actual_headers)

    def _check_response_core(self) -> (bool, str):
        res, msg = self._check_response_headers()
        if not res:
            return (res, msg)
        if self.expected.type == "json":
            return self._check_response_json()
        elif self.expected.type == "jsonpath":
            return self._check_response_jsonpath()
        elif self.expected.type == "content":
            return self._check_response_content()
        else:
            return (
                False,
                f"Unknown Expected Type: {self.expected.type}\n",
            )

    def _check_response(self) -> (bool, str):
        if self.expected.code == self.response.status_code:
            return self._check_response_core()
        else:
            return (
                False,
                f"Expected Code: {self.expected.code} Actual Code: {self.response.status_code}\n",
            )

    def validate(
        self, response: requests.Response, expected: Expected, id: str, api: API
    ) -> (bool, str):
        self.response = response
        self.expected = expected
        self.id = id
        self.api = api
        self._prepare_expected_headers()
        self._prepare_expected_text()
        self._prepare_expected_results()
        return self._check_response()
