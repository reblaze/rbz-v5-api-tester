from typing import Any
from dataclasses import dataclass
from rbz_api_tester.utils import read_json
from rbz_api_tester.CommonParameters import CommonParameters


@dataclass
class API:
    base: str
    path: str
    trim_trailing_slash: bool

    @staticmethod
    def from_dict(obj: Any) -> "API":
        try:
            _base = str(API.api_from_alias(obj.get("Base")))
            _trim = bool(API.trim_from_alias(obj.get("Base")))
        except:
            _base = str(obj.get("Base"))
            if obj.get("Trim") is not None:
                _trim = bool(obj.get("Trim"))
            else:
                _trim = False
        _path = str(obj.get("Path"))

        return API(_base, _path, _trim)

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

    def available_api(self, clean: bool) -> []:
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
        if self.trim_trailing_slash:
            return f"{trimmed_base}/{trimmed_path}".rstrip("/")
        else:
            return f"{trimmed_base}/{trimmed_path}"
