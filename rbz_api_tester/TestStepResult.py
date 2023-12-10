from rbz_api_tester.Result import Result


class TestStepResult:
    result: Result
    error_message: str

    def __init__(self):
        self.result = Result.NotPerformed
        self.error_message = ""
