from asyncio import LimitOverrunError
from logging import INFO
from pathlib import Path
import shutil
import tarfile
import logging
import colorlog
import subprocess
import os

from logger import logger, LogLevel

class Student:
    def __init__(self, archive: Path, parent_directory: Path):
        self.archive: Path = archive
    
        # Assuming archive is formatted like this: lastfirst_#_#_project.tar.gz
        self.name: str = self.archive.stem.split("_")[0]

        self.directory: StudentDirectory | None = StudentDirectory(name = self.name)
        self.directory.create_directory(parent_directory)

        self.readme: Path | None = None
        self.makefile: Path | None = None
        self.program: Path | None = None

    def extract (self, gzip=True) -> None:
        if self.create_directory():
            if tarfile.is_tarfile(self.archive):
                mode: str = "r:gz" if gzip else "r"
                with tarfile.open(self.archive, mode) as archive:
                    archive.extractall(path=self.directory, filter="tar")

                    entries = Student._directory_entries(self.directory)
                    if len(entries) == 1 and entries[0].is_dir():
                        self._collapse()

        return

    def get_readme(self) -> str:
        if self.readme is None:
            readmes = [ readme for readme in self.directory.glob("README*") ]
            if len(readmes) != 0:
                self.readme = readmes[0]
            else:
                logger.announce(f"{self.name}´s README not found.", LogLevel.WARNING)
                return ""

        text = self.readme.read_text()

        return text

    def make (self) -> None:
        if self.makefile is None:
            makefiles = [ file for file in self.directory.entries() if file.is_file() and file.name.lower() == "makefile" ]
            if len(makefiles) != 0:
                self.makefile = makefiles[0]
                logger.announce(f"{logger.BOLD}{self.name}'s Makefile{logger.RESET} (path: {self.makefile})", LogLevel.INFO)

            else:
                logger.announce(f"{self.name}'s Makefile not found.'", LogLevel.ERROR)
                # raise MakefileNotFoundError("Makefile not found")
                raise Exception("Makefile not found.")

        try:
            make_result = subprocess.run(
                ["make", "-f", self._makefile],
                cwd=self.directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
        except Exception as e:
            logger.announce(f"{logger.BOLD}{self.name}'s Make{logger.RESET} could not run.", LogLevel.ERROR)
            # raise MakeError(f"Make could not run")
            raise Exception("Makefile could not run.")

        if make_result.returncode != 0:
            logger.announce(f"Make did not run successfuly.", LogLevel.ERROR)
            print(f"{logger.BOLD}Make error:{logger.RESET}\n{make_result.stdout}")
            # raise MakeError(f"Make did not run successfully.")
            raise Exception(f"Make did not run successfully.")
        else:
            logger.announce(f"{self.name}'s Makefile ran successfully.", LogLevel.SUCCESS)

        return




class StudentDirectory:
    def __init__(self, name: str):
        self.name: str = name
        self.directory: Path | None = None

    def create_directory(self, parent_directory: Path) -> bool:
        location: Path = parent_directory / self.name

        try:
            location.mkdir()
            logger.announce(f"Successfully created directory '{self.name}'.", LogLevel.NOTE)
            self.directory = location

            return True
        except FileExistsError:
            logger.announce(f"Directory '{self.name}' already exists; skipping.", LogLevel.NOTE)
            self.directory = location

            return False
        except Exception as exception:
            logger.announce(f"Could not create new directory '{self.name}': {exception}.", LogLevel.ERROR)
            self.directory = None

            raise

    def entries(self, ignores: list[str] = [".DS_Store", ".git"]) -> list[Path]:
        entries: list[Path] = list(self.directory.iterdir())

        return [ entry for entry in entries if entry.name not in ignores ]

    def collapse(self, ignores: list[str] = [".DS_Store", ".git"]):
        """
        Collapse the (potentially) nested directory entries into a single directory.
        :param ignores: Files to ignore when collapsing
        :return:
        """
        current: Path = self.directory

        while current.is_dir():
            entries = Student._directory_entries(directory=current, ignores=ignores)

            if len(entries) == 1 and entries[0].is_dir():
                current = entries[0]
            else:
                break

        for file in current.iterdir():
            shutil.move(str(file), str(self.directory))

        return
