from typing import Any
from dataclasses import dataclass
from rbz_api_tester.utils import read_json
from rbz_api_tester.CommonParameters import CommonParameters


@dataclass
class API:
    base: str
    path: str

    @staticmethod
    def from_dict(obj: Any) -> "API":
        try:
            _base = str(API.api_from_alias(obj.get("Base")))
        except:
            _base = str(obj.get("Base"))
        _path = str(obj.get("Path"))

        return API(_base, _path)

    def to_dict(self) -> dict:
        try:
            _api = self.alias_from_api(self.base)
        except:
            _api = self.base
        return {
            "Base": _api,
            "Path": self.path,
        }

    @staticmethod
    def api_from_alias(alias_str: str) -> str:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["alias"] == alias_str:
                return api["API"]
        raise Exception(f"mapping does not contain alias: {alias_str}")

    @staticmethod
    def trim_from_alias(alias_str: str) -> bool:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["alias"] == alias_str:
                return api["trim-trailing-slash"]
        raise Exception(f"mapping does not contain alias: {alias_str}")

    @staticmethod
    def trim_from_api(api_str: str) -> bool:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["API"] == api_str:
                return api["trim-trailing-slash"]
        raise Exception(f"mapping does not contain API: {api_str}")

    @staticmethod
    def items_from_alias(alias_str: str) -> bool:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["alias"] == alias_str:
                return api["items"]
        raise Exception(f"mapping does not contain alias: {alias_str}")

    @staticmethod
    def items_from_api(api_str: str) -> bool:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["API"] == api_str:
                return api["items"]
        raise Exception(f"mapping does not contain API: {api_str}")

    def alias_from_api(self, api_str: str) -> str:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["API"] == api_str:
                return api["alias"]
        raise Exception(f"mapping does not contain api: {api_str}")

    def template_from_alias(self, alias_str: str) -> str:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["alias"] == alias_str:
                return api["template"]
        raise Exception(f"mapping does not contain alias: {alias_str}")

    def defaults_from_alias(self, alias_str: str) -> str:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["alias"] == alias_str:
                return api["defaults"]
        raise Exception(f"mapping does not contain alias: {alias_str}")

    def template_from_api(self, api_str: str) -> str:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["API"] == api_str:
                return api["template"]
        raise Exception(f"mapping does not contain api: {api_str}")

    def defaults_from_api(self, api_str: str) -> str:
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if api["API"] == api_str:
                return api["defaults"]
        raise Exception(f"mapping does not contain api: {api_str}")

    def available_api(self, clean: bool) -> list[str]:
        res = []
        apis = read_json(CommonParameters.api_mapping)
        for api in apis["api-to-alias"]:
            if bool(api["clean"]) == clean:
                res.append(api["API"])
        return res

    def is_send_traffic(self):
        return self.base == "@@traffic@@"

    def get(self) -> str:
        trimmed_base = self.base.rstrip("/")
        trimmed_path = self.path.lstrip("/")
        if API.trim_from_api(self.base):
            return f"{trimmed_base}/{trimmed_path}".rstrip("/")
        else:
            return f"{trimmed_base}/{trimmed_path}"
