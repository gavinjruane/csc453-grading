from collections.abc import Generator

from exceptions import *
from config import *
from test import Test

from pathlib import Path
import shutil
import tarfile
import logging
import colorlog
import subprocess
import os

class Student:
    students_directory: Path = Path()

    def __init__ (self, archive: Path):
        self.archive: Path = archive
        
        # Assuming archive is formatted like this: lastfirst_#_#_project.tar.gz
        self.name: str = self.archive.stem.split("_")[0]

        self.directory: Path | None = None
        self._readme: Path | None = None
        self._makefile: Path | None = None
        self._program: Path | None = None

    @classmethod
    def iter_from_directory (cls, submissions: Path) -> Generator["Student", None, None]:
        for archive in submissions.iterdir():
            yield cls(archive)

    @classmethod
    def list_from_directory (cls, submissions: Path) -> list["Student"]:
        return [ cls(archive) for archive in submissions.iterdir() ]

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

    @classmethod
    def _directory_entries (cls, directory: Path, ignores: list[str] | None = [".DS_Store", ".git"]):
        entries = list(directory.iterdir())

        return [ entry for entry in entries if entry.name not in ignores ]

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
        

    def readme (self, print_text=True) -> str:
        if self._readme is None:
            readmes = [ readme for readme in self.directory.glob("README*") ]
            if len(readmes) != 0:
                self._readme = readmes[0]
            else:
                log.warning(f"{self.name}´s README not found.")
                return ""

        text = self._readme.read_text()
        if print_text: print(text)

        return text

    def make (self) -> None:
        if self._makefile is None:
            makefiles = [ file for file in self.directory.iterdir() if file.is_file() and file.name.lower() == "makefile" ]
            if len(makefiles) != 0:
                self._makefile = makefiles[0]
                log.info(f"{BOLD}{self.name}'s Makefile{RESET} (path: {self._makefile})")

            else:
                log.error(f"{self.name}'s Makefile not found.'")
                raise MakefileNotFoundError("Makefile not found")

        try:
            make_result = subprocess.run(
                ["make", "-f", self._makefile],
                cwd=self.directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
        except Exception as e:
            log.error(f"{BOLD}{self.name}'s Make{RESET} could not run.")
            raise MakeError(f"Make could not run")

        if make_result.returncode != 0:
            log.error(f"Make did not run successfuly.")
            print(f"{BOLD}Make error:{RESET}\n{make_result.stdout}")
            raise MakeError(f"Make did not run successfully.")
        else:
            log.info(f"{self.name}'s Makefile ran successfully.")

        return
            
    def run (self, arguments: list[str] = [], look_for: str = "", capture_output: bool = False, find_program: bool = False) -> Tuple[bool, str]:
        if self._program is None:
            if look_for != "":
                programs = [ program for program in self.directory.iterdir() if program.is_file() and os.access(program, os.X_OK) and program.name == look_for ]
            else:
                programs = [ program for program in self.directory.iterdir() if program.is_file() and os.access(program, os.X_OK) ]
            if len(programs) != 0:
                self._program = programs[0]
                log.info(f"{BOLD}{self.name}'s program{RESET} (path: {self._program})")
            else:
                log.error(f"{self.name}'s program not found.")
                raise ProgramNotFoundError("Program not found.")

        if find_program:
            arguments.insert(0, str(self._program))

        try:
            if capture_output:
                program_result = subprocess.run(
                    arguments,
                    cwd=self.directory
                )
            else:
                program_result = subprocess.run(
                    arguments,
                    cwd=self.directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
        except Exception as e:
            log.error(f"{BOLD}{self.name}'s program{RESET} could not run due to exception {e}.")
            raise ProgramError("Program could not run.")
        
        if program_result.returncode != 0:
            log.error(f"{self.name}'s program did not run successfully.'")

            return (False, program_result.stdout)
        else:
            log.info(f"{self.name}'s program ran successfully.")

            return (True, program_result.stdout)

    def test (self, tests: list["Test"]) -> dict[]:
        outputs: dict[] = {}
        
        for test in tests:
            outputs[test] = self.run(test.command, capture_output=True)

        return outputs
                    
            
        
