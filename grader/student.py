import subprocess
import tarfile
from pathlib import Path
from typing import Literal

from grader.directory import resolve_directory, get_directory_entries, collapse
from logger import logger


class Student:
    def __init__(self, archive: Path, parent_directory: Path):
        self.archive: Path = archive
    
        # Assuming archive is formatted like this: lastfirst_#_#_project.tar.gz
        self.name: str = self.archive.stem.split("_")[0]

        self.directory: Path = resolve_directory(
            directory=None,
            root=parent_directory,
            fallback=self.name
        )

        self.readme: Path | None = None
        self.makefile: Path | None = None
        self.program: Path | None = None

    def extract (self, gzip=True) -> None:
        if tarfile.is_tarfile(self.archive):
            mode: Literal["r", "r:gz"] = "r:gz" if gzip else "r"
            with tarfile.open(self.archive, mode) as archive:
                archive.extractall(path=self.directory, filter="tar")

                entries = get_directory_entries(self.directory)
                if len(entries) == 1 and entries[0].is_dir():
                    collapse(self.directory)

        return

    def get_readme(self) -> str:
        if self.readme is None:
            readmes = [ readme for readme in self.directory.glob("README*") ]
            if len(readmes) != 0:
                self.readme = readmes[0]
            else:
                logger.error(f"{self.name}´s README not found.")
                return ""

        text = self.readme.read_text()

        return text

    def make(self) -> None:
        if self.makefile is None:
            makefiles = [ file for file in get_directory_entries(self.directory) if file.is_file() and file.name.lower() == "makefile" ]
            if len(makefiles) != 0:
                self.makefile = makefiles[0]
                logger.info(f"{self.name}'s Makefile was found (path: {self.makefile}).")
            else:
                logger.error(f"{self.name}'s Makefile was not found.")
                # raise MakefileNotFoundError("Makefile not found")
                raise Exception("Makefile not found.")

        try:
            if self.makefile is not None:
                make_result = subprocess.run(
                    args=["make", "-f", self.makefile],
                    cwd=self.directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            else:
                raise Exception("Makefile not found.")
        except Exception as e:
            logger.error(f"{self.name}'s Makefile did not run.")
            # raise MakeError(f"Make could not run")
            raise Exception(f"Makefile could not run {e}.")

        if make_result.returncode != 0:
            logger.warning(f"{self.name}'s Makefile failed to run successfully.")
            logger.info(make_result.stdout)
            # raise MakeError(f"Make did not run successfully.")
            raise Exception(f"Make did not run successfully.")
        else:
            logger.info(f"{self.name}'s Makefile ran successfully.")

        return

