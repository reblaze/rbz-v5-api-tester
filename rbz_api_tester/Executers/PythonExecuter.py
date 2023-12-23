import subprocess

from rbz_api_tester.utils import get_my_external_ip
from rbz_api_tester.CommonParameters import CommonParameters


class PythonExecuter:
    def execute(self, py_code) -> (int, str, str):
        code = ""
        for code_line in py_code:
            code = f"{code}\n{code_line}"
        code = (
            code.replace("@@planet@@", CommonParameters.planet)
            .replace("@@ip@@", get_my_external_ip())
            .replace("@@branch@@", CommonParameters.branch)
            .replace("@@api_key@@", CommonParameters.api_key)
            .replace("@@email@@", CommonParameters.email)
        )
        CommonParameters.logger.debug(f"\t\tPython Script:\n{code}")

        process = subprocess.Popen(
            ["python"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        stdout, stderr = process.communicate(input=code)
        if stdout != "":
            CommonParameters.logger.debug(f"\t\tOutput:\n{stdout}")
        if stderr != "":
            CommonParameters.logger.debug(f"\t\tError:\n{stderr}")

        return (process.returncode, stdout, stderr)
