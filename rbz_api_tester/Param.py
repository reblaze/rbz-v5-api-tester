from typing import List
from typing import Any
from dataclasses import dataclass


@dataclass
class Param:
    key: str
    value: Any

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    @staticmethod
    def from_dict(obj: Any) -> "Param":
        _key = str(obj.get("Key"))
        _value = obj.get("Value")
        return Param(_key, _value)

    def to_dict(self) -> dict:
        return {"Key": self.key, "Value": self.value}
