import tarfile
import tomllib
import zipfile
from pathlib import Path
from typing import Generator

from grader.configuration import Configuration
from grader.logger import logger, LogColor
from grader.student import Student
from grader.directory import resolve_directory
from grader.test import Test, Given


def students(submissions_directory: Path, outputs_directory: Path, givens_directory: Path) -> Generator[
    Student, None, None]:
    for archive in submissions_directory.iterdir():
        yield Student(
            archive=archive,
            parent_directory=outputs_directory,
            givens=givens(givens_directory)
        )


def givens(givens_directory: Path) -> list[Given]:
    return [Given(name=given.name, givens_directory=givens_directory) for given in givens_directory.iterdir()]


def tests(tests_directory: Path) -> list[Test]:
    return [Test(name=test.name, tests_directory=tests_directory) for test in tests_directory.iterdir()]


class Project:
    def __init__(self, config_file: str):
        with open(config_file, "rb") as config:
            config_file = tomllib.load(config)
            try:
                self.config = Configuration.model_validate(config_file)
            except:
                logger.critical("Invalid config file. Did you follow the schema?")
                raise Exception("Invalid config file")

        self.name = self.config.name

        current_directory = Path(__file__).resolve().parent
        self.root_directory = Path(
            self.config.root_directory).resolve() if self.config.root_directory else current_directory

        self.submissions_directory: Path = resolve_directory(
            directory=self.config.submissions.directory if self.config.submissions else None,
            root=self.root_directory,
            fallback="submissions"
        )

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
            self.tests: list[Test] = tests(self.tests_directory)
            logger.info(f"Found tests at {self.tests_directory} and imported them")

            self.givens_directory: Path | None = resolve_directory(
                directory=self.config.tests.givens_directory if self.config.tests else None,
                root=self.root_directory,
                fallback="givens",
                create_on_fail=False
            )
            self.givens: list[Given] = givens(self.givens_directory)
            logger.info(f"Found givens at {self.givens_directory} and imported them")
        else:
            self.tests_directory: Path | None = None
            self.givens_directory: Path | None = None

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

    def grade(self, wait_after_step=False, wait_at_end=False) -> None:
        WAIT_AFTER_STEP = f"{LogColor.BOLD}Press any key to continue...{LogColor.RESET}\n"
        WAIT_AT_END = f"{LogColor.BOLD}Press any key to continue to the next student...{LogColor.RESET}\n"

        for student in students(submissions_directory=self.submissions_directory,
                                outputs_directory=self.outputs_directory,
                                givens_directory=self.givens_directory):
            student.extract()
            if wait_after_step: input(WAIT_AFTER_STEP)

            print(student.get_readme())
            if wait_after_step: input(WAIT_AFTER_STEP)

            try:
                student.make()
            except Exception as e:
                logger.warning(f"Make finished unsuccessfully: {e}")
                continue
            if wait_after_step: input(WAIT_AFTER_STEP)

            try:
                student.find_program(look_for=self.config.submissions.program)
            except Exception as e:
                logger.warning(f"Find program finished unsuccessfully: {e}")
                continue
            if wait_after_step: input(WAIT_AFTER_STEP)

            result, output = student.run(
                arguments=self.tests[0].command,
                capture_output=True,
                insert_program_name=False
            )
            logger.info(f"Student {student.name} finished with result: {result}")
            logger.info(f"Student {student.name} finished with output: {output}")
            if wait_after_step: input(WAIT_AFTER_STEP)

            if wait_at_end: input(WAIT_AT_END)
            print("\n\n")


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
