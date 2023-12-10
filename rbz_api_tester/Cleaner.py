import requests
from typing import List
from logging import Logger


class Cleaner:
    api_key: str
    planet: str
    planet_url: str
    apis: List[str]
    ids: List[str]
    logger: Logger

    def __init__(self, api_key: str, planet: str, ids: List[str], logger: Logger):
        self.api_key = api_key
        self.planet = planet
        self.planet_url = f"{self.planet}.dev.app.reblaze.io"

        self.apis = [
            "/conf/api/v3/configs/prod/d/aclprofiles/",
            "/conf/api/v3/configs/prod/d/actions/",
            "/reblaze/api/v3/reblaze/configs/prod/d/backends/",
            "/reblaze/api/v3/reblaze/configs/prod/d/cloud-functions/",
            "/conf/api/v3/configs/prod/d/contentfilterprofiles/",
            "/conf/api/v3/configs/prod/d/contentfilterrules/",
            "/reblaze/api/v3/reblaze/configs/prod/d/dynamic-rules/",
            "/conf/api/v3/configs/prod/d/flowcontrol/",
            "/conf/api/v3/configs/prod/d/globalfilters/",
            "/reblaze/api/v3/reblaze/configs/prod/d/proxy-templates/",
            "/conf/api/v3/configs/prod/d/ratelimits/",
            "/reblaze/api/v3/reblaze/configs/prod/d/routing-profiles/",
            "/conf/api/v3/configs/prod/d/securitypolicies/",
            "/reblaze/api/v3/reblaze/configs/prod/d/sites/",
        ]

        self.ids = ids
        self.logger = logger

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

            final_url = f"{api}e/{id}/"
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
            final_api_url = f"https://{self.planet_url}{api}"
            res, ids = self.get_ids(final_api_url)
            if res:
                for id in ids:
                    if str(id).startswith("api_tester_") or id in self.ids:
                        if self.delete(final_api_url, id):
                            self.logger.debug(f"api: {api} deleted: {id}")
                        else:
                            self.logger.error(f"api: {api} failed to delete: {id}")
