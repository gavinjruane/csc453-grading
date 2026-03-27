import shutil
from pathlib import Path

from grader.logger import logger

def resolve_directory(
        directory: str | None,
        root: Path = Path(__file__).resolve().parent,
        fallback: str = "",
        create_on_fail: bool = True
) -> Path:
    """
    Attempts to resolve the location of a directory. A new directory can be created if it doesn't exist.
    :param create_on_fail:
    :param directory: Path (or name) of the directory to look for
    :param root: Root directory of the project
    :param fallback: Fallback name in the event that the directory doesn't exist
    :return: A Path object representing the location of the found/new directory
    """
    if directory is None:
        new_directory = root / fallback
    else:
        new_directory = Path(directory).resolve()

    try:
        if not new_directory.exists():
            if create_on_fail:
                logger.info(f"Creating new directory at {new_directory}")
                new_directory.mkdir()
            else:
                logger.warning(f"No new directory created at {new_directory}.")
        else:
            logger.info(f"Found directory at {new_directory}")
    except:
        logger.error(f"Could not create new directory at {new_directory}")
        raise Exception(f"Could not create new directory at {new_directory}")

    return new_directory


def copy_to_directory(directory: Path, item: Path) -> None:
    shutil.copy(str(item), str(directory))


def collapse(directory: Path, ignores: list[str] = [".DS_Store", ".git"]):
    """
    Collapse the (potentially) nested directory entries into a single directory.
    :param directory: Directory to collapse
    :param ignores: Files to ignore when collapsing
    :return:
    """
    current: Path | None = directory
    if current is None:
        return

    while current.is_dir():
        entries = get_directory_entries(directory=current, ignores=ignores)

        if len(entries) == 1 and entries[0].is_dir():
            current = entries[0]
        else:
            break

    for file in current.iterdir():
        try:
            shutil.move(str(file), str(directory))
        except:
            logger.error(f"Could not move {file}")
            raise Exception(f"Could not move {file}")

    return


def get_directory_entries(directory: Path, ignores: list[str] = [".DS_Store", ".git"]) -> list[Path]:
    """
    Returns the entries in the specified directory
    :param directory: Directory to retrieve entries from
    :param ignores: Files to ignore in the returned entry list
    :return: List of entries in directory
    """
    entries: list[Path] = list(directory.iterdir())

    return [entry for entry in entries if entry.name not in ignores]