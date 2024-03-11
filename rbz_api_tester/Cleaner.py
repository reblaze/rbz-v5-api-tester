import requests
from typing import List

from rbz_api_tester.API import API
from rbz_api_tester.CommonParameters import CommonParameters


DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"


class Cleaner:
    apis: List[str]
    ids: List[str]

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Basic {CommonParameters.api_key}",
            "User-Agent": DEFAULT_UA,
            "planet-name": f"{CommonParameters.planet}",
            "planet-hostname": f"{CommonParameters.planet_url}",
            "Content-Type": "application/json",
        }

    def __init__(self, ids: List[str]):
        self.ids = ids
        self.apis = API("", "").available_api(True)

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Basic {CommonParameters.api_key}",
            "User-Agent": DEFAULT_UA,
            "planet-name": f"{CommonParameters.planet}",
            "planet-hostname": f"{CommonParameters.planet_url}",
            "Content-Type": "application/json",
        }

    def get_ids(self, api: str, items: str):
        try:
            results = []
            response = requests.get(api, headers=self.headers)
            if response.status_code == 200:
                elements = response.json()
                if items != "":
                    elements = elements[items]
                for element in elements:
                    results.append(element["id"])
                return True, results
            else:
                return False, []
        except requests.exceptions.RequestException as e:
            return False, []

    def delete(self, api: str, id: str) -> bool:
        try:
            delete_url = f"{api}/{id}"
            response = requests.delete(delete_url, headers=self.headers)
            SUCCESS_RESPONSES = (
                {"ok": True},
                {"message": "Successfully deleted entry"},
            )
            if response.status_code == 200 and response.json() in SUCCESS_RESPONSES:
                return True
            elif response.status_code == 204:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            return False

    def execute(self):
        for api in self.apis:
            _api = API(base=api, path="")
            branch_api = _api.get().replace("@@branch@@", CommonParameters.branch)
            final_api_url = f"https://{CommonParameters.planet_url}{branch_api}"
            if API.trim_from_api(api):
                final_api_url = final_api_url.rstrip("/")
            elif final_api_url[-1] != "/":
                final_api_url = f"{final_api_url}/"
            res, ids = self.get_ids(final_api_url, API.items_from_api(api))
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
