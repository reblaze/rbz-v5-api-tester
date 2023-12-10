import requests
from typing import List
from logging import Logger
from rbz_api_tester.utils import available_api


class Cleaner:
    api_key: str
    planet: str
    branch:str
    planet_url: str
    apis: List[str]
    ids: List[str]
    logger: Logger

    def __init__(self, api_key: str, planet: str, branch: str, ids: List[str], logger: Logger):
        self.api_key = api_key
        self.planet = planet
        self.branch = branch
        self.planet_url = f"{self.planet}.dev.app.reblaze.io"
        self.ids = ids
        self.logger = logger
        self.apis = available_api(True)

    def get_ids(self, api: str):
        try:
            results = []
            headers = {
                "Authorization": f"Basic {self.api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                "planet-name": f"{self.planet}",
                "planet-hostname": f"{self.planet_url}",
                "Content-Type": "application/json",
            }

            response = requests.get(api, headers=headers)
            if response.status_code == 200:
                elements = response.json()
                for element in elements:
                    results.append(element["id"])
                return True, results
            else:
                return False, []
        except requests.exceptions.RequestException as e:
            return False, []

    def delete(self, api: str, id: str):
        try:
            headers = {
                "Authorization": f"Basic {self.api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                "planet-name": f"{self.planet}",
                "planet-hostname": f"{self.planet_url}",
                "Content-Type": "application/json",
            }

            final_url = f"{api}/e/{id}/"
            response = requests.delete(final_url, headers=headers)
            if response.status_code == 200 and response.json()["ok"]:
                return True
            elif response.status_code == 204:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            return False

    def execute(self):
        for api in self.apis:
            branch_api = api.replace("@@branch@@", self.branch)
            final_api_url = f"https://{self.planet_url}{branch_api}/"
            res, ids = self.get_ids(final_api_url)
            if res:
                for id in ids:
                    if str(id).startswith("api_tester_") or id in self.ids:
                        if self.delete(final_api_url, id):
                            self.logger.debug(f"api: {final_api_url} deleted: {id}")
                        else:
                            self.logger.error(f"api: {final_api_url} failed to delete: {id}")
