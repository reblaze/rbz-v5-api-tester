import json
import requests
from urllib.parse import urlparse, parse_qsl
from rbz_api_tester.Expected import Expected
from rbz_api_tester.Payload import Payload
from rbz_api_tester.TestSuite import TestSuite
from rbz_api_tester.Test import Test
from rbz_api_tester.TestStep import TestStep
from rbz_api_tester.TestStep import Param
from rbz_api_tester.utils import read_json
from rbz_api_tester.CommonParameters import CommonParameters
from rbz_api_tester.API import API
from haralyzer import HarParser
from typing import List


class TestBuilder:
    def extract_api(self, request: requests.Request, apis: []) -> (str, str):
        for api in apis:
            if api in request["url"]:
                index = request["url"].find(api)
                if index != -1:
                    path = request["url"][index + len(api) :]
                    return (api, path.lstrip("/"))
        return (None, None)

    def extract_query_params(self, request: requests.Request) -> []:
        parsed_url = urlparse(request["url"])
        return parse_qsl(parsed_url.query)

    def extract_args(self, request: requests.Request) -> []:
        return json.loads(request["postData"]["text"])

    def translate(self):
        mime_types = [
            "text/plain",
            "text/html",
            "text/json",
            "text/xml",
            "application/octet-stream",
            "application/pdf",
            "application/zip",
            "application/msword",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/json",
            "application/xml",
            "application/xhtml+xml",
        ]

        request_types_with_no_quotes = (int, bool, float)
        response_types_with_no_quotes = (int, bool, float)
        dummy_api = API("", "")
        apis1 = dummy_api.available_api(False)
        index = 0
        for api in apis1:
            apis1[index] = api.replace("@@branch@@", CommonParameters.branch)
            index = index + 1

        apis2 = dummy_api.available_api(True)
        index = 0
        for api in apis2:
            apis2[index] = api.replace("@@branch@@", CommonParameters.branch)
            index = index + 1

        apis = list(set(apis1) | set(apis2))
        apis.remove("@@traffic@@")

        parser: HarParser = HarParser(read_json(CommonParameters.har_file))
        # Parse the HAR data
        har_data = parser.har_data

        test_suite = TestSuite("Add your test suite name here", False)
        test = Test("Add your test name here", False)
        test.steps = list()
        for entry in har_data["entries"]:
            api, path = self.extract_api(entry["request"], apis)
            if api is None:
                continue

            response = entry["response"]
            mime_type = str(entry["response"]["content"]["mimeType"])

            if mime_type not in mime_types:
                continue

            api = api.replace(CommonParameters.branch, "@@branch@@")
            actual_api = API(dummy_api.alias_from_api(api), path)
            method = entry["request"]["method"]
            if method == "GET" or method == "DELETE":
                args = self.extract_query_params(entry["request"])
            if method == "POST" or method == "PUT":
                args = self.extract_args(entry["request"])

            step = TestStep("Add your step name here", False)
            step.type = "request"
            step.api = actual_api
            step.method = method

            if method == "POST" or method == "PUT":
                if len(args) > 0:
                    step.payload = Payload()
                    for arg in args.items():
                        val = None
                        if isinstance(arg[1], request_types_with_no_quotes):
                            val = arg[1]
                        else:
                            val = f'"{arg[1]}"'
                        step.payload.params.append(Param(arg[0], val))

            elif method == "GET" or method == "DELETE":
                if len(args) > 0:
                    step.arguments = list()
                    for arg in args:
                        val = None
                        if isinstance(arg[1], request_types_with_no_quotes):
                            val = arg[1]
                        else:
                            val = f'"{arg[1]}"'
                        step.arguments.append(Param(arg[0], val))

            step.expected = Expected()
            step.expected.code = int(response["status"])
            if response["content"]["mimeType"] == "application/json":
                step.expected.type = "json"
                response_json = json.loads(response["content"]["text"])
                if type(response_json) is list:
                    step.expected.single = False
                    for item in response_json:
                        results = list()
                        for key, value in item.items():
                            val = None
                            if isinstance(value, response_types_with_no_quotes):
                                val = value
                            else:
                                val = str(value)
                            param = Param(key, val)
                            results.append(param)
                        step.expected.multiple_results.append(results)
                else:
                    step.expected.single = True
                    for key, value in response_json.items():
                        val = None
                        if isinstance(value, response_types_with_no_quotes):
                            val = value
                        else:
                            val = str(value)
                        param = Param(key, val)
                        step.expected.single_result.append(param)
            else:
                step.expected.type = "text"
                step.expected.single = True
                step.expected.text = response["content"]["text"]

            test.steps.append(step)

        test_suite.tests.append(test)
        with open(f"{CommonParameters.tests_folder}/my_suite.json", "w") as output_file:
            content = json.dumps(test_suite.to_dict(), indent=4, sort_keys=False)
            output_file.write(content)
            output_file.close()
