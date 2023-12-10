import requests
from typing import Any
from logging import Logger

from rbz_api_tester.Payload import Payload

class ApiExecuter:
    api_key: str
    planet: str
    planet_url: str
    headers: Any
    logger: Logger

    def __init__(self, api_key: str, planet: str, headers: Any, logger: Logger):
        self.api_key = api_key
        self.planet = planet
        self.planet_url = f"{planet}.dev.app.reblaze.io"
        self.headers = headers
        self.logger = logger

    def _add_custom_headers(self, headers):
        if self.headers is not None:
            for item in self.headers:
                headers[item.key] = item.value

    def _add_common_headers(self, headers):
        headers["Authorization"] = f"Basic {self.api_key}"
        headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        headers["planet-name"] = f"{self.planet}"
        headers["planet-hostname"] = f"{self.planet_url}"
        headers["Content-Type"] = "application/json"

    def get(self, api):
        headers = {}
        self.logger.debug(f"\t\tMethod is GET")
        self._add_common_headers(headers)
        self._add_custom_headers(headers)
        final_api_url = f"https://{self.planet_url}{api}"
        self.logger.debug(f"\t\tCalling: {final_api_url}")
        response = requests.get(final_api_url, headers=headers)
        self.logger.debug(f"\t\tResponse Code: {response.status_code}")
        self.logger.debug(f"\t\tResponse: {response.text}")
        return response


    def send(self, api):
        headers = {}
        self.logger.debug(f"\t\tMethod is GET")
        self._add_custom_headers(headers)
        final_api_url = f"https://{api}"
        self.logger.debug(f"\t\tCalling: {final_api_url}")
        response = requests.get(final_api_url, headers=headers, verify=False)
        self.logger.debug(f"\t\tResponse Code: {response.status_code}")
        self.logger.debug(f"\t\tResponse: {response.text}")
        return response


    def delete(self, api):
        headers = {}
        self._add_common_headers(headers)
        self._add_custom_headers(headers)
        self.logger.debug(f"\t\tMethod is DELETE")
        final_api_url = f"https://{self.planet_url}{api}"
        self.logger.debug(f"\t\tCalling: {final_api_url}")
        response = requests.delete(final_api_url, headers=headers)
        self.logger.debug(f"\t\tResponse Code: {response.status_code}")
        self.logger.debug(f"\t\tResponse: {response.text}")
        return response

    def post(self, api, payload: Payload):
        headers = {}
        self._add_common_headers(headers)
        self._add_custom_headers(headers)
        self.logger.debug(f"\t\tMethod is POST")
        final_api_url = f"https://{self.planet_url}{api}"
        self.logger.debug(f"\t\tCalling: {final_api_url} with payload: {payload}")
        response = requests.post(final_api_url, json=payload, headers=headers)
        self.logger.debug(f"\t\tResponse Code: {response.status_code}")
        self.logger.debug(f"\t\tResponse: {response.text}")
        return response

    def put(self, api, payload: Payload):
        headers = {}
        self._add_common_headers(headers)
        self._add_custom_headers(headers)
        self.logger.debug(f"\t\tMethod is PUT")
        final_api_url = f"https://{self.planet_url}{api}"
        self.logger.debug(f"\t\tCalling: {final_api_url} with payload: {payload}")
        response = requests.put(final_api_url, json=payload, headers=headers)
        self.logger.debug(f"\t\tResponse Code: {response.status_code}")
        self.logger.debug(f"\t\tResponse: {response.text}")
        return response
