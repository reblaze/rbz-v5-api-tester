import os
import requests
import json
from typing import Any
from pathlib import Path

from rbz_api_tester.API import API
from rbz_api_tester.Payload import Payload
from rbz_api_tester.Time import convert_time_macros
from rbz_api_tester.utils import get_my_external_ip, generate_uuid
from rbz_api_tester.CommonParameters import CommonParameters


class ApiExecuter:
    generate_id: bool
    headers: Any
    arguments: Any
    files: Any
    api: API
    method: str
    payload: Payload

    def __init__(
        self,
        generate_id: bool,
        headers: Any,
        arguments: Any,
        files: Any,
        api: API,
        method: str,
        payload: Payload,
    ):
        self.generate_id = generate_id
        self.headers = headers
        self.arguments = arguments
        self.files = files
        self.api = api
        self.method = method
        self.payload = payload

    def get_traffic_url(self) -> str:
        api = API(base=API.api_from_alias("api-dns"), path="")
        response = self._get(api.get())
        if response.status_code != 200 or response.reason != "OK":
            return ""

        json = response.json()
        for dns_record in json["dns_records"]:
            if dns_record["type"] == "A" and CommonParameters.branch in str(
                dns_record["name"]
            ):
                return str(dns_record["name"]).rstrip(".")

        return ""

    def _prepare_params(self):
        if self.arguments is not None:
            for arg in self.arguments:
                arg.value = arg.value.replace("@@branch@@", CommonParameters.branch)
                arg.value = arg.value.replace("@@ip@@", get_my_external_ip())

    def _prepare_payload(self, id: str):
        if self.payload is None:
            return None

        template_file = os.path.join(
            Path(CommonParameters.templates_folder).resolve(),
            self.api.template_from_api(self.api.base),
        )
        defaults_file = os.path.join(
            Path(CommonParameters.defaults_folder).resolve(),
            self.api.defaults_from_api(self.api.base),
        )
        templates_contents = Path(template_file).read_text()

        if id is not None:
            templates_contents = templates_contents.replace("@@id@@", id)

        for param in self.payload.params:
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

        templates_contents = templates_contents.replace(
            "@@branch@@", CommonParameters.branch
        )
        templates_contents = templates_contents.replace(
            "@@planet@@", CommonParameters.planet
        )
        templates_contents = templates_contents.replace(
            "@@api_key@@", CommonParameters.api_key
        )
        templates_contents = templates_contents.replace("@@ip@@", get_my_external_ip())

        return json.loads(templates_contents)

    def _prepare_url(self, id):
        final_api_url = self.api.get()
        if id is not None:
            final_api_url = final_api_url.replace("@@id@@", id)
        final_api_url = final_api_url.replace("@@branch@@", CommonParameters.branch)
        final_api_url = final_api_url.replace("@@ip@@", get_my_external_ip())
        return final_api_url

    def _add_custom_headers(self, headers):
        if self.headers is not None:
            for item in self.headers:
                headers[item.key] = item.value

    def _add_common_headers(self, headers):
        headers["Authorization"] = f"Basic {CommonParameters.api_key}"
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        )
        headers["planet-name"] = f"{CommonParameters.planet}"
        headers["planet-hostname"] = f"{CommonParameters.planet_url}"
        headers["Content-Type"] = "application/json"
        headers["X-Auth-User"] = f"{CommonParameters.email}"

    def _add_arguments(self, params):
        if self.arguments is not None:
            for item in self.arguments:
                params[item.key] = item.value

    def _add_files(self, files):
        if self.files is not None:
            for item in self.files:
                files[item.key] = open(item.value, "rb")

    def _get_id(self) -> str:
        id = None
        if self.generate_id:
            id = generate_uuid()
        elif self.payload is not None:
            for param in self.payload.params:
                if param.key == "id":
                    id = param.value
                    break
        return id

    def _get(self, api):
        headers = {}
        params = {}
        CommonParameters.logger.debug(f"\t\tMethod is GET")
        self._add_common_headers(headers)
        self._add_custom_headers(headers)
        self._add_arguments(params)
        final_api_url = f"https://{CommonParameters.planet_url}{api}"
        CommonParameters.logger.debug(f"\t\tCalling: {final_api_url}")
        if len(params) > 0:
            final_api_url = f"{final_api_url.rstrip('/')}"
        response = requests.get(final_api_url, headers=headers, params=params)
        CommonParameters.logger.debug(f"\t\tResponse Code: {response.status_code}")
        CommonParameters.logger.debug(f"\t\tResponse: {response.text}")
        return response

    def _send(self, api, method):
        headers = {}
        params = {}
        files = {}
        CommonParameters.logger.debug(f"\t\tMethod is {method}")
        self._add_custom_headers(headers)
        self._add_arguments(params)
        self._add_files(files)
        final_api_url = f"https://{api}"
        CommonParameters.logger.debug(f"\t\tCalling: {final_api_url}")
        if method == "GET":
            response = requests.get(
                final_api_url, headers=headers, params=params, verify=False
            )
        elif method == "POST":
            response = requests.post(
                final_api_url, headers=headers, data=params, files=files, verify=False
            )
        elif method == "PUT":
            response = requests.put(
                final_api_url, headers=headers, data=params, files=files, verify=False
            )
        elif method == "DELETE":
            response = requests.delete(
                final_api_url, headers=headers, params=params, verify=False
            )
        elif method == "PATCH":
            response = requests.patch(
                final_api_url, headers=headers, data=params, files=files, verify=False
            )
        elif method == "OPTIONS":
            response = requests.options(final_api_url, headers=headers, verify=False)
        elif method == "HEAD":
            response = requests.head(final_api_url, headers=headers, verify=False)
        else:
            raise Exception(f"unknown method: {method}")
        CommonParameters.logger.debug(f"\t\tResponse Code: {response.status_code}")
        CommonParameters.logger.debug(f"\t\tResponse: {response.text}")
        return response

    def _delete(self, api):
        headers = {}
        self._add_common_headers(headers)
        self._add_custom_headers(headers)
        CommonParameters.logger.debug(f"\t\tMethod is DELETE")
        final_api_url = f"https://{CommonParameters.planet_url}{api}"
        CommonParameters.logger.debug(f"\t\tCalling: {final_api_url}")
        response = requests.delete(final_api_url, headers=headers)
        CommonParameters.logger.debug(f"\t\tResponse Code: {response.status_code}")
        CommonParameters.logger.debug(f"\t\tResponse: {response.text}")
        return response

    def _post(self, api, payload: Payload):
        headers = {}
        params = {}
        self._add_common_headers(headers)
        self._add_custom_headers(headers)
        self._add_arguments(params)
        CommonParameters.logger.debug(f"\t\tMethod is POST")
        final_api_url = f"https://{CommonParameters.planet_url}{api}"
        CommonParameters.logger.debug(
            f"\t\tCalling: {final_api_url} with payload: {payload}"
        )
        response = requests.post(
            final_api_url, json=payload, headers=headers, data=params
        )
        CommonParameters.logger.debug(f"\t\tResponse Code: {response.status_code}")
        CommonParameters.logger.debug(f"\t\tResponse: {response.text}")
        return response

    def _put(self, api, payload: Payload):
        headers = {}
        params = {}
        self._add_common_headers(headers)
        self._add_custom_headers(headers)
        self._add_arguments(params)
        CommonParameters.logger.debug(f"\t\tMethod is PUT")
        final_api_url = f"https://{CommonParameters.planet_url}{api}"
        CommonParameters.logger.debug(
            f"\t\tCalling: {final_api_url} with payload: {payload}"
        )
        response = requests.put(
            final_api_url, json=payload, headers=headers, data=params
        )
        CommonParameters.logger.debug(f"\t\tResponse Code: {response.status_code}")
        CommonParameters.logger.debug(f"\t\tResponse: {response.text}")
        return response

    def execute(self) -> (str, requests.Response):
        id = None
        if self.arguments is not None:
            for arg in self.arguments:
                arg.value = convert_time_macros(arg.value)

        if self.api.is_send_traffic():
            self._prepare_params()
            final_api = self.api.get().replace(
                "@@traffic@@", CommonParameters.traffic_url
            )
            return (id, self._send(final_api, self.method))
        elif self.method == "POST":
            id = self._get_id()
            final_api_url = self._prepare_url(id)
            actual_payload = self._prepare_payload(id)
            return (id, self._post(final_api_url, actual_payload))
        elif self.method == "PUT":
            id = self._get_id()
            final_api_url = self._prepare_url(id)
            actual_payload = self._prepare_payload(id)
            return (id, self._put(final_api_url, actual_payload))
        elif self.method == "GET":
            id = self._get_id()
            self._prepare_params()
            final_api_url = self._prepare_url(id)
            return (id, self._get(final_api_url))
        elif self.method == "DELETE":
            id = self._get_id()
            self._prepare_params()
            final_api_url = self._prepare_url(id)
            return (id, self._delete(final_api_url))
        else:
            raise Exception(
                f"Unsupported method: {self.method}, expected GET, POST, PUT, DELETE"
            )
