from pathlib import Path
import shutil
import tarfile
import logging
import colorlog
import subprocess
import os

class Student:
    def __init__(self, archive: Path):
        self.archive: Path = archive
    
        # Assuming archive is formatted like this: lastfirst_#_#_project.tar.gz
        self.name: str = self.archive.stem.split("_")[0]

        self.directory: Path | None = None
        self.readme: Path | None = None
        self.makefile: Path | None = None
        self.program: Path | None = None

    def extract (self, gzip=True) -> None:
        # if self.create_directory():
        #     if tarfile.is_tarfile(self.archive):
        #         mode: str = "r:gz" if gzip else "r"
        #         with tarfile.open(self.archive, mode) as archive:
        #             archive.extractall(path=self.directory, filter="tar")

        #             entries = Student._directory_entries(self.directory)
        #             if len(entries) == 1 and entries[0].is_dir():
        #                 self._collapse()

        return
    
    def create_directory (self) -> bool:
        directory = self.students_directory / self.name

        try:
            directory.mkdir()
            log.info(f"Successfully created directory '{self.name}'.")
            self.directory = directory

            return True
        except FileExistsError:
            log.info(f"Directory '{self.name}' already exists; skipping.")
            self.directory = directory

            return False
        except Exception as exception:
            log.error(f"Could not create new directory '{self.name}'.")
            self.directory = None

            raise
        

    def _collapse (self, ignores: list[str] | None = [".DS_Store", ".git"]):
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


