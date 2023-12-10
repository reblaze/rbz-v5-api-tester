from typing import Any
from dataclasses import dataclass
from rbz_api_tester.utils import from_alias, from_api

@dataclass
class API:
    base: str
    path: str

    @staticmethod
    def from_dict(obj: Any) -> "API":
        try:
            _base = str(from_alias(obj.get("Base")))
        except:
            _base = str(obj.get("Base"))
        _path = str(obj.get("Path"))

        return API(_base, _path)

    def to_dict(self) -> dict:
        try:
            _api = from_api(self.base)
        except:
            _api = self.base
        return {
            "Base": _api,
            "Path": self.path,
        }

    def get(self) -> str:
        trimmed_base = self.base.rstrip("/")
        trimmed_path = self.path.lstrip("/")

        return f"{trimmed_base}/{trimmed_path}"