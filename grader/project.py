import tarfile
import tomllib
import zipfile
from pathlib import Path
from typing import Generator

from grader.configuration import Configuration
from grader.logger import logger, LogColor
from grader.student import Student
from grader.directory import collapse, resolve_directory


def students(submissions_directory: Path, outputs_directory: Path) -> Generator[Student, None, None]:
    for archive in submissions_directory.iterdir():
        yield Student(
            archive=archive,
            parent_directory=outputs_directory
        )


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

        self.tests_directory: Path = resolve_directory(
            directory=self.config.tests.directory if self.config.tests else None,
            root=self.root_directory,
            fallback="tests",
            create_on_fail=False
        )

        self.submissions_archive: Path = Path(self.config.submissions.archive_filename)
        if self.submissions_archive.exists():
            logger.info(f"Found archive at {self.submissions_archive}")
            logger.info(f"Unpacking archive at {self.submissions_archive}")
            unpack_archive(
                archive=self.submissions_archive,
                destination=self.submissions_directory,
                type=self.config.submissions.archive_type
            )
        else:
            logger.critical(f"No archive at {self.submissions_archive}")
            raise Exception(f"No archive at {self.submissions_archive}")

    def grade(self, wait=False):
        for student in students(submissions_directory=self.submissions_directory,
                                outputs_directory=self.outputs_directory):
            student.extract()
            print(student.get_readme())
            if wait: input(f"{LogColor.BOLD}Press any key to continue...{LogColor.RESET}")
            print("\n\n")


def unpack_archive(archive: Path, destination: Path, type: str = "tar.gz") -> None:
    """
    Unpack an archive to a destination.
    :param archive: Path to the archive
    :param destination: Destination to unpack the archive into
    :param type: Type of the archive (zip or tar.gz)
    :return: None
    """
    match type:
        case "tar.gz":
            if tarfile.is_tarfile(archive):
                with tarfile.open(archive) as tar:
                    tar.extractall(destination)
        case "zip":
            if zipfile.is_zipfile(archive):
                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(path=destination)
