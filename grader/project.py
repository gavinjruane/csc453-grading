import tarfile
import tomllib
import zipfile
from pathlib import Path
from unittest import case

from grader.configuration import Configuration
from grader.logger import logger


# def submissions(submissions: Path) -> Generator[object, None, None]:
#     for archive in submissions.iterdir():
#         yield Student(archive=archive)


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


def resolve_directory(directory: str | None, root: Path = Path(__file__).resolve().parent, fallback: str = "") -> Path:
    """
    Attempts to resolve the location of a directory. A new directory can be created if it doesn't exist.
    :param directory: Path (or name) of the directory to look for
    :param root: Root directory of the project
    :param fallback: Fallback name in the event that the directory doesn't exist
    :return: A Path object representing the location of the found/new directory
    """
    if directory is None:
        new_directory = root / fallback
    else:
        new_directory = Path(directory).resolve()

    if not new_directory.exists():
        logger.info(f"Creating new directory at {new_directory}")
        new_directory.mkdir()
    else:
        logger.info(f"Found directory at {new_directory}")

    return new_directory


def unpack_archive(archive: Path, destination: Path, type: str = "tar.gz") -> None:
    match type:
        case "tar.gz":
            if tarfile.is_tarfile(archive):
                with tarfile.open(archive) as tar:
                    tar.extractall(destination)
        case "zip":
            if zipfile.is_zipfile(archive):
                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(path=destination)
