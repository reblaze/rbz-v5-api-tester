from typing import List
from typing import Any
from dataclasses import dataclass

from rbz_api_tester.Param import Param


@dataclass
class Payload:
    params: List[Param]

    def __init__(self, params: List[Param] = None):
        if params is None:
            self.params = list()
        else:
            self.params = params

    @staticmethod
    def from_dict(obj: Any) -> "Payload":
        _params = [Param.from_dict(y) for y in obj.get("Params")]
        return Payload(_params)

    def to_dict(self) -> dict:
        return {
            "Params": [param.to_dict() for param in self.params],
        }
