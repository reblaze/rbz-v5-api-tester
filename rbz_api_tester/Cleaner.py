import requests
from typing import List

from rbz_api_tester.API import API
from rbz_api_tester.CommonParameters import CommonParameters


class Cleaner:
    apis: List[str]
    ids: List[str]

    def __init__(self, ids: List[str]):
        self.ids = ids
        self.apis = API("", "").available_api(True)

    def get_ids(self, api: str):
        try:
            results = []
            headers = {
                "Authorization": f"Basic {CommonParameters.api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                "planet-name": f"{CommonParameters.planet}",
                "planet-hostname": f"{CommonParameters.planet_url}",
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
                "Authorization": f"Basic {CommonParameters.api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                "planet-name": f"{CommonParameters.planet}",
                "planet-hostname": f"{CommonParameters.planet_url}",
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
            branch_api = api.replace("@@branch@@", CommonParameters.branch)
            final_api_url = f"https://{CommonParameters.planet_url}{branch_api}/"
            res, ids = self.get_ids(final_api_url)
            if res:
                for id in ids:
                    if str(id).startswith("api_tester_") or id in self.ids:
                        if self.delete(final_api_url, id):
                            CommonParameters.logger.debug(
                                f"api: {final_api_url} deleted: {id}"
                            )
                        else:
                            CommonParameters.logger.error(
                                f"api: {final_api_url} failed to delete: {id}"
                            )
