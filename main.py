import argparse
import logging
import os

from logging import Logger
from pathlib import Path
from rbz_api_tester.TestBuilder import TestBuilder
from rbz_api_tester.Tester import Tester
from rbz_api_tester.Cleaner import Cleaner
from rbz_api_tester.Executers.ApiExecuter import ApiExecuter
from rbz_api_tester.CommonParameters import CommonParameters
from rbz_api_tester.Result import Result
from rbz_api_tester.utils import get_cluster


def set_logger(log_file: str, planet: str) -> Logger:
    os.environ["PYTHONIOENCODING"] = "utf-8"
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.DEBUG)
    log = ""
    if log_file is not None:
        log = log_file
    else:
        log = f"./log/API-Tester-{planet}.log"

    if os.path.exists(log):
        os.remove(log)

    if not os.path.exists(f"./log/"):
        os.mkdir(f"./log/")

    file_handler = logging.FileHandler(log, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)-8s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def enumerate_files(dir: str):
    files = []
    folder = Path(dir).resolve()
    file_list = folder.glob("*")
    for file in file_list:
        if file.is_file():  # Check if it's a regular file (not a directory)
            files.append(str(file.resolve()))
    return files


def run_test_suits():
    try:
        CommonParameters.logger.info(
            "-------------------------------- starting new run --------------------------------"
        )
        tester = Tester()
        ids = set()
        test_suite_files = enumerate_files(CommonParameters.tests_folder)
        CommonParameters.logger.debug("Test Suites Files:")
        CommonParameters.logger.debug("\n".join(test_suite_files))

        num_of_test_suites = len(test_suite_files)

        results = []

        for test_suite_file in test_suite_files:
            suite_ids = tester.get_special_ids(str(test_suite_file))
            ids = ids.union(suite_ids)
            result = tester.execute(str(test_suite_file))
            results.append(result)
            if result.result != Result.Skipped and cleanup:
                CommonParameters.logger.info(f"Performing Cleanup...")
                cleaner = Cleaner(ids=ids)
                cleaner.execute()

        CommonParameters.logger.info(
            f"---------------------------------  Summary --------------------------------"
        )
        CommonParameters.logger.info(f"Total Test Suites: {num_of_test_suites}")
        CommonParameters.logger.info(f"Passed Test Suites: {tester.passed_test_suites}")
        CommonParameters.logger.info(f"Failed Test Suites: {tester.failed_test_suites}")
        CommonParameters.logger.info(
            f"Skipped Test Suites: {tester.skipped_test_suites}"
        )
        CommonParameters.logger.info(
            f"--------------------------- details on failures ---------------------------"
        )
        tester.failure_report(results)
        CommonParameters.logger.info(
            f"---------------------------------------------------------------------------"
        )
        return
    except Exception as e:
        CommonParameters.logger.error(
            f"Application terminated abnormally due to exception:\n{repr(e)}"
        )
        cleanup_only()


def cleanup_only():
    tester = Tester()
    ids = set()
    test_suite_files = enumerate_files(CommonParameters.tests_folder)
    for test_suite_file in test_suite_files:
        suite_ids = tester.get_special_ids(str(test_suite_file))
        ids = ids.union(suite_ids)

    CommonParameters.logger.info(f"Performing Cleanup...")
    cleaner = Cleaner(ids=ids)
    cleaner.execute()


def translate():
    builder = TestBuilder()
    builder.translate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--planet", required=False, help="Name of test planet")
    parser.add_argument("-b", "--branch", required=True, help="Name of branch")
    parser.add_argument("-t", "--api_token", required=False, help="API token")
    parser.add_argument("-e", "--email", required=False, help="API owner email")
    parser.add_argument(
        "-c",
        "--cleanup",
        required=False,
        action="store_true",
        help="Cleanup after test",
    )
    parser.add_argument(
        "-o",
        "--output_log_file",
        required=False,
        help="Location and name of the desired output log file",
    )
    parser.add_argument(
        "-x",
        "--cleanup_only",
        required=False,
        action="store_true",
        help="Only Cleanup (run no tests)",
    )
    parser.add_argument(
        "-i", "--input_file", required=False, help="har file to translate"
    )

    args = parser.parse_args()

    CommonParameters.har_file = args.input_file
    CommonParameters.planet = args.planet
    CommonParameters.planet_url = f"{CommonParameters.planet}.dev.app.reblaze.io"
    CommonParameters.branch = args.branch
    CommonParameters.api_key = args.api_token
    CommonParameters.email = args.email
    output = None
    cleanup = args.cleanup

    if args.output_log_file is not None:
        output = args.output_log_file

    CommonParameters.defaults_folder = "./defaults"
    CommonParameters.templates_folder = "./templates"
    CommonParameters.tests_folder = "./test_suites"
    CommonParameters.api_mapping = "./metadata/api-map.json"
    CommonParameters.cluster_mapping = "./metadata/cluster-map.json"
    CommonParameters.shared_steps = "./shared-steps/shared-steps.json"
    CommonParameters.control_cluster_name = get_cluster("control")
    CommonParameters.data_cluster_name = get_cluster("data")
    CommonParameters.broker_cluster_name = get_cluster("broker")

    CommonParameters.logger = set_logger(output, args.planet)

    if args.cleanup_only:
        cleanup_only()
    elif CommonParameters.har_file is not None:
        translate()
    else:
        CommonParameters.traffic_url = ApiExecuter(
            generate_id=False,
            headers=None,
            arguments=None,
            files=None,
            api=None,
            method=None,
            payload=None,
        ).get_traffic_url()
        run_test_suits()
