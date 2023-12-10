from enum import Enum


class Result(Enum):
    NotPerformed = -1
    Passed = 0
    Failed = 1
    Skipped = 2
