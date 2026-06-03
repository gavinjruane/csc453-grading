import tarfile
import tomllib
import zipfile
from pathlib import Path
from typing import Generator

from grader.configuration import Configuration
from grader.logger import logger, LogColor
from grader.student import Student
from grader.directory import resolve_directory
from grader.test import Test, Given, ProcessState, TestState, TestType

WAIT_AFTER_STEP = f"{LogColor.BOLD}Press any key to continue...{LogColor.RESET}\n"
WAIT_AT_END = f"{LogColor.BOLD}Press any key to continue to the next student...{LogColor.RESET}\n"

# def students(submissions_directory: Path, outputs_directory: Path, givens: list[Given], tests: list[Test]
#              ) -> Generator[Student, None, None]:
#     for archive in submissions_directory.iterdir():
#         yield Student(
#             archive=archive,
#             parent_directory=outputs_directory,
#             givens=givens,
#             tests=tests
#         )

def students(submissions_directory: Path, outputs_directory: Path, givens: list[Given], tests: list[Test]) -> list[Student]:
    return sorted([Student(archive=archive, parent_directory=outputs_directory, givens=givens, tests=tests) for archive in submissions_directory.iterdir()], key=lambda student: student.name)


def givens(givens_directory: Path) -> list[Given]:
    return sorted([Given(name=given.name, givens_directory=givens_directory) for given in givens_directory.iterdir()], key=lambda given: given.name)


def tests(tests_directory: Path) -> list[Test]:
    return sorted([Test(name=test.name, tests_directory=tests_directory) for test in tests_directory.iterdir()], key=lambda test: test.name)


class Project:
    def __init__(self, config_file: str, timeout: int | None = None):
        self.failures = []
        self.partials = []
        self.successes = []

        with open(config_file, "rb") as config:
            config_file = tomllib.load(config)
            try:
                self.config = Configuration.model_validate(config_file)
            except:
                logger.critical("Invalid config file. Did you follow the schema?")
                raise Exception("Invalid config file")

        self.name = self.config.name
        self.timeout = timeout if timeout is not None else self.config.tests.timeout

        current_directory = Path(__file__).resolve().parent
        self.root_directory = Path(
            self.config.root_directory).resolve() if self.config.root_directory else current_directory

        self.submissions_directory: Path = resolve_directory(
            directory=self.config.submissions.directory if self.config.submissions else None,
            root=self.root_directory,
            fallback="submissions"
        )
        self.languages: list[str] = self.config.submissions.languages

        self.outputs_directory: Path = resolve_directory(
            directory=self.config.outputs.directory if self.config.outputs else None,
            root=self.root_directory,
            fallback="outputs"
        )

        if self.config.tests:
            self.tests_directory: Path | None = resolve_directory(
                directory=self.config.tests.directory if self.config.tests else None,
                root=self.root_directory,
                fallback="tests",
                create_on_fail=False
            )
            if self.config.tests.directory:
                self.tests: list[Test] | None = tests(self.tests_directory)
                logger.info(f"Found tests at {self.tests_directory} and imported them")
            else:
                self.tests: list[Test] | None = None
                logger.info(f"No tests found/included.")

            self.givens_directory: Path | None = resolve_directory(
                directory=self.config.tests.givens_directory if self.config.tests else None,
                root=self.root_directory,
                fallback="givens",
                create_on_fail=False
            )
            if self.config.tests.givens_directory:
                self.givens: list[Given] | None = givens(self.givens_directory)
                logger.info(f"Found givens at {self.givens_directory} and imported them")
            else:
                self.givens: list[Given] | None = None
                logger.info(f"No givens found/included.")
        else:
            self.tests_directory: Path | None = None
            self.givens_directory: Path | None = None
            self.tests = None
            self.givens = None

        self.submissions_archive: Path = Path(self.config.submissions.archive_filename)
        if self.submissions_archive.exists():
            logger.info(f"Found archive at {self.submissions_archive}")
            logger.info(f"Unpacking archive at {self.submissions_archive}")
            unpack_archive(
                archive=self.submissions_archive,
                destination=self.submissions_directory,
                archive_type=self.config.submissions.archive_type
            )
        else:
            logger.critical(f"No archive at {self.submissions_archive}")
            raise Exception(f"No archive at {self.submissions_archive}")

    def grade(
            self,
            wait_after_step=False,
            wait_at_end=False,
            allow_skips=False,
            print_results=False,
            check_language=False
    ) -> None:
        for student in students(submissions_directory=self.submissions_directory,
                                outputs_directory=self.outputs_directory,
                                givens=self.givens,
                                tests=self.tests):

            print(f"\n{LogColor.BOLD}Student {student.name}{LogColor.RESET}")
            if allow_skips:
                key = input(f"Press \"s\" to skip {student.name}...")
                if key.lower() == "s":
                    continue

            student.extract()

            print('\n' + student.get_readme())
            if check_language:
                student.language = input("Is this a Python or C program? ")

            if student.language == "C":
                try:
                    student.make()
                except Exception as e:
                    logger.warning(f"Make finished unsuccessfully: {e}")
                    self.failures.append(student)
                    continue
                if wait_after_step: input(WAIT_AFTER_STEP)

            try:
                student.find_program(look_for=self.config.submissions.programs,
                                     preferred_program=self.config.submissions.preferred_program,
                                     type=self.config.submissions.type)
            except Exception as e:
                logger.warning(f"Find program finished unsuccessfully: {e}")
                self.failures.append(student)
                continue
            if wait_after_step: input(WAIT_AFTER_STEP)

            # TODO: fix this to make it workable for non-test based projects
            if self.tests is not None:
                for test in self.tests:
                    use_diff: bool = True if test.type == TestType.DIFF else False
                    result = student.test(test, timeout=self.timeout, print_test=True, use_diff=use_diff,
                                          print_stdout=True, html_diff=use_diff)
                    if result["run_result"] == ProcessState.SUCCESS:
                        logger.debug(f"Student {student.name} test finished successfully.")
                        if use_diff:
                            if not result["diff"]:
                                logger.info(f"Student {student.name} files differ.")
                                logger.debug(f"Student {student.name} html file: {result["html_file"]}.")
                                student.test_results[test.name] = TestState.DIFF_MISMATCH
                            else:
                                logger.info(f"Student {student.name} files match.")
                                student.test_results[test.name] = TestState.DIFF_MATCH
                        else:
                            if not result["other"]:
                                logger.info(f"Student {student.name} test did not pass. (Might need manual inspection.)")
                                student.test_results[test.name] = TestState.FAILURE
                            else:
                                logger.info(f"Student {student.name} test passed. (Might need manual inspection.)")
                                student.test_results[test.name] = TestState.SUCCESS
                    elif result["run_result"] == ProcessState.FAILURE:
                        logger.debug(f"Student {student.name} test did not finish successfully.")
                        student.test_results[test.name] = TestState.INCOMPLETE
                    elif result["run_result"] == ProcessState.TIMEOUT:
                        logger.debug(f"Student {student.name} test timed out.")
                        student.test_results[test.name] = TestState.TIMEOUT
                    else:
                        logger.debug(f"Student {student.name} test finished with an unexpected error code.")
                        student.test_results[test.name] = TestState.FAILURE
                    if wait_after_step: input(WAIT_AFTER_STEP)

            if print_results and self.tests is not None:
                print(f"{LogColor.BOLD}{student.name}'s results:{LogColor.RESET}")
                print(student.results())

            if wait_at_end: input(WAIT_AT_END)
            print("\n\n")

        return


def unpack_archive(archive: Path, destination: Path, archive_type: str = "tar.gz") -> None:
    """
    Unpack an archive to a destination.
    :param archive: Path to the archive
    :param destination: Destination to unpack the archive into
    :param archive_type: Type of the archive (zip or tar.gz)
    :return: None
    """
    match archive_type:
        case "tar.gz":
            if tarfile.is_tarfile(archive):
                with tarfile.open(archive) as tar:
                    tar.extractall(destination)
        case "zip":
            if zipfile.is_zipfile(archive):
                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(path=destination)
