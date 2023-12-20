from typing import List
from typing import Any
from dataclasses import dataclass

from rbz_api_tester.Param import Param


@dataclass
class Payload:
    # template: str
    # defaults: str
    params: List[Param]

    @staticmethod
    def from_dict(obj: Any) -> "Payload":
        #        _template = str(obj.get("Template"))
        #        _defaults = str(obj.get("Defaults"))
        _params = [Param.from_dict(y) for y in obj.get("Params")]
        # return Payload(_template, _defaults, _params)
        return Payload(_params)

    def to_dict(self) -> dict:
        return {
            #           "Template": self.template,
            #           "Defaults": self.defaults,
            "Params": [param.to_dict() for param in self.params],
        }
