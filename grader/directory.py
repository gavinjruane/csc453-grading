import shutil
from pathlib import Path

from grader.logger import logger


def get_directory_entries(directory: Path, ignores: list[str] = [".DS_Store", ".git"]) -> list[Path]:
    entries: list[Path] = list(directory.iterdir())

    return [entry for entry in entries if entry.name not in ignores]


class Directory:
    def __init__(self, name: str):
        self.name: str = name
        self.path: Path = Path()

    def create_directory(self, parent_directory: Path) -> bool:
        location: Path = parent_directory / self.name

        try:
            location.mkdir()
            logger.info(f"Successfully created directory '{self.name}'.")
            self.path = location

            return True
        except FileExistsError:
            logger.info(f"Directory '{self.name}' already exists; skipping.")
            self.path = location

            return False
        except Exception as exception:
            logger.error(f"Could not create new directory '{self.name}': {exception}.")
            self.path = Path()

            raise

    def entries(self, ignores: list[str] = [".DS_Store", ".git"]) -> list[Path]:
        """
        Get a list of entries present in the directory
        :param ignores: Files to ignore when searching
        :return: A list of entries in the directory
        """
        if self.path is not None:
            return get_directory_entries(self.path, ignores)
        else:
            return []

    def collapse(self, ignores: list[str] = [".DS_Store", ".git"]):
        """
        Collapse the (potentially) nested directory entries into a single directory.
        :param ignores: Files to ignore when collapsing
        :return:
        """
        current: Path | None = self.path
        if current is None:
            return

        while current.is_dir():
            entries = get_directory_entries(directory=current, ignores=ignores)

            if len(entries) == 1 and entries[0].is_dir():
                current = entries[0]
            else:
                break

        for file in current.iterdir():
            shutil.move(str(file), str(self.path))

        return
