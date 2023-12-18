import argparse
import logging
import os

from pathlib import Path
from rbz_api_tester.ApiTester import ReblazeApiTester
from rbz_api_tester.Cleaner import Cleaner

def set_logger(log_file: str, planet: str):
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

    file_handler = logging.FileHandler(log)
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


def main():
    logger.info(
        "-------------------------------- starting new run --------------------------------"
    )
    tester = ReblazeApiTester(
        templates_folder, defaults_folder, planet_name, branch_name, api_key, logger
    )
    ids = set()
    test_suite_files = enumerate_files(tests_folder)
    logger.debug("Test Suites Files:")
    logger.debug("\n".join(test_suite_files))

    num_of_test_suites = len(test_suite_files)

    results = []

    for test_suite_file in test_suite_files:
        suite_ids = tester.get_special_ids(str(test_suite_file))
        ids = ids.union(suite_ids)
        results.append(tester.execute(str(test_suite_file)))
        if cleanup:
            logger.info(f"Performing Cleanup...")
            cleaner = Cleaner(
                api_key=api_key,
                planet=planet_name,
                branch=branch_name,
                ids=ids,
                logger=logger,
            )
            cleaner.execute()

    logger.info(
        f"---------------------------------  Summary --------------------------------"
    )
    logger.info(f"Total Test Suites: {num_of_test_suites}")
    logger.info(f"Passed Test Suites: {tester.passed_test_suites}")
    logger.info(f"Failed Test Suites: {tester.failed_test_suites}")
    logger.info(f"Skipped Test Suites: {tester.skipped_test_suites}")
    logger.info(
        f"--------------------------- details on failures ---------------------------"
    )
    tester.failure_report(results)
    logger.info(
        f"---------------------------------------------------------------------------"
    )

    #assert (
    #    tester.failed_test_suites == 0
    #), f"{tester.failed_test_suites} test suites failed"


def cleanup_only():
    tester = ReblazeApiTester(
        templates_folder, defaults_folder, planet_name, branch_name, api_key, logger
    )
    ids = set()
    test_suite_files = enumerate_files(tests_folder)
    for test_suite_file in test_suite_files:
        suite_ids = tester.get_special_ids(str(test_suite_file))
        ids = ids.union(suite_ids)

    logger.info(f"Performing Cleanup...")
    cleaner = Cleaner(
        api_key=api_key,
        planet=planet_name,
        branch=branch_name,
        ids=ids,
        logger=logger,
    )
    cleaner.execute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--planet", required=True, help="Name of test planet")
    parser.add_argument("-b", "--branch", required=True, help="Name of branch")
    parser.add_argument("-t", "--api_token", required=True, help="API token")
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
    args = parser.parse_args()

    planet_name = args.planet
    branch_name = args.branch
    api_key = args.api_token
    output = None
    cleanup = args.cleanup

    if args.output_log_file is not None:
        output = args.output_log_file

    defaults_folder = "./defaults"
    templates_folder = "./templates"
    tests_folder = "./test_suites"

    logger = set_logger(args.output_log_file, args.planet)

    if args.cleanup_only:
        cleanup_only()
    else:
        main()
