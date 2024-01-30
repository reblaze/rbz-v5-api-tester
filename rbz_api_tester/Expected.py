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
    headers: List[Param]
    single_result: List[Param]
    multiple_results: List[List[Param]]

    def __init__(
        self,
        code: str = None,
        type: str = None,
        text: str = None,
        single: bool = True,
        headers: List[Param] = None,
        single_result: List[Param] = None,
        multiple_results: List[List[Param]] = None,
    ):
        self.code = code
        self.type = type
        self.text = text
        self.single = single
        if headers is None:
            self.headers = list()
        else:
            self.headers = headers

        if single_result is None:
            self.single_result = list()
        else:
            self.single_result = single_result

        if multiple_results is None:
            self.multiple_results = list()
        else:
            self.multiple_results = multiple_results

    @staticmethod
    def from_dict(obj: Any) -> "Expected":
        _code = int(obj.get("Code"))
        _type = str(obj.get("Type"))
        _single = bool(obj.get("Single"))
        _headers = None
        _multiple_results = None
        _single_result = None
        _text = None

        if obj.get("Headers") is not None:
            _headers = [Param.from_dict(h) for h in obj.get("Headers")]

        if obj.get("MultipleResults") is not None:
            _multiple_results = [
                [Param.from_dict(param_dict) for param_dict in result_list]
                for result_list in obj.get("MultipleResults", [])
            ]
        elif obj.get("SingleResult") is not None:
            _single_result = [Param.from_dict(y) for y in obj.get("SingleResult")]
        else:
            _text = str(obj.get("Text"))

        return Expected(
            _code, _type, _text, _single, _headers, _single_result, _multiple_results
        )

    def to_dict(self) -> dict:
        _multiple_results = None
        _single_result = None
        _text = None
        _headers = None

        result = {
            "Code": self.code,
            "Type": self.type,
            "Single": self.single,
        }

        if self.headers is not None:
            result["Headers"] = [header.to_dict() for header in self.headers]

        if not self.single:
            result["MultipleResults"] = [
                [param.to_dict() for param in result_list]
                for result_list in self.multiple_results
            ]
        elif self.single and self.text is None:
            result["SingleResult"] = [result.to_dict() for result in self.single_result]
        else:
            result["Text"] = self.text

        return result
