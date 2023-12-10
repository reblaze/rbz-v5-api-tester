from typing import List
from typing import Any
from dataclasses import dataclass

from rbz_api_tester.Param import Param


@dataclass
class Expected:
    code: int
    type: str
    text: str
    single: bool
    single_result: List[Param]
    multiple_results: List[List[Param]]

    @staticmethod
    def from_dict(obj: Any) -> "Expected":
        _code = int(obj.get("Code"))
        _type = str(obj.get("Type"))
        _single = bool(obj.get("Single"))
        _multiple_results = None
        _single_result = None
        _text = None
        if obj.get("MultipleResults") is not None:
            _multiple_results = [
                [Param.from_dict(param_dict) for param_dict in result_list]
                for result_list in obj.get("MultipleResults", [])
            ]
        elif obj.get("SingleResult") is not None:
            _single_result = [Param.from_dict(y) for y in obj.get("SingleResult")]
        else:
            _text = str(obj.get("Text"))

        return Expected(_code, _type, _text, _single, _single_result, _multiple_results)

    def to_dict(self) -> dict:
        _multiple_results = None
        _single_result = None
        _text = None

        if not self.single:
            _multiple_results = [
                [param.to_dict() for param in result_list]
                for result_list in self.multiple_results
            ]
        elif self.single and self.text is None:
            _single_result = [result.to_dict() for result in self.single_result]
        else:
            _text = self.text

        return {
            "Code": self.code,
            "Type": self.type,
            "Text": _text,
            "Single": self.single,
            "MultipleResults": _multiple_results,
            "SingleResult": _single_result,
        }
