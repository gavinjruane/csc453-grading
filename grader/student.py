import difflib
import os
import subprocess
import tarfile
from pathlib import Path
from typing import Literal

from grader.directory import resolve_directory, get_directory_entries, collapse, copy_to_directory
from grader.logger import LogColor
from grader.test import Test, Given
from logger import logger


class Student:
    def __init__(self, archive: Path, parent_directory: Path, givens: list[Given]):
        self.archive: Path = archive

        # Assuming archive is formatted like this: lastfirst_#_#_project.tar.gz
        self.name: str = self.archive.stem.split("_")[0]

        self.directory: Path = resolve_directory(
            directory=None,
            root=parent_directory,
            fallback=self.name
        )
        for given in givens:
            copy_to_directory(self.directory, given.path)

        self.readme: Path | None = None
        self.makefile: Path | None = None
        self.program: Path | None = None

    def extract(self, gzip=True) -> None:
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
            readmes = [readme for readme in self.directory.glob("README*")]
            if len(readmes) != 0:
                self.readme = readmes[0]
            else:
                logger.error(f"{self.name}´s README not found.")
                return ""

        text = self.readme.read_text()

        return text

    def make(self) -> None:
        if self.makefile is None:
            makefiles = [file for file in get_directory_entries(self.directory) if
                         file.is_file() and file.name.lower() == "makefile"]
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

    def find_program(self, look_for: str | None):
        if look_for is not None:
            programs = [program for program in self.directory.iterdir() if
                        program.is_file() and os.access(program, os.X_OK) and program.name == look_for]
        else:
            programs = [program for program in self.directory.iterdir() if
                        program.is_file() and os.access(program, os.X_OK)]
        if len(programs) != 0:
            self.program = programs[0]
            logger.info(f"{self.name}'s program (path: {self.program})")
        else:
            logger.error(f"{self.name}'s program not found.")
            raise Exception("Program not found.")

    def run(self,
            timeout: int,
            arguments: list[str] | None = None,
            print_stdout: bool = False,
            insert_program_name: bool = True,
            ) -> tuple[bool, list[str]]:
        global process

        if arguments is None:
            arguments = [self.program]

        if insert_program_name:
            arguments.insert(0, str(self.program))

        captured_output: list[str] = []
        try:
            process = subprocess.Popen(
                arguments,
                cwd=self.directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                if print_stdout: print(line, end="")
                captured_output.append(line)

            process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            logger.error(f"{self.name}'s program timed out.")
            process.kill()
        except Exception as e:
            logger.error(f"{LogColor.BOLD}{self.name}'s program{LogColor.RESET} could not run due to exception {e}.")
            raise Exception("Program could not run.")

        if process.returncode != 0:
            logger.warning(f"{self.name}'s program did not run successfully.'")

            return False, captured_output
        else:
            logger.debug(f"{self.name}'s program ran successfully.")

            return True, captured_output

    def test(self,
             test: Test,
             timeout: int,
             print_test: bool = False,
             use_diff: bool = False,
             html_diff: bool = False,
             print_stdout: bool = False
             ) -> dict:
        result = {}

        if print_test:
            print(test)

        result["run_result"] = self.run(
            timeout=timeout,
            arguments=test.command,
            print_stdout=print_stdout,
            insert_program_name=False
        )
        process_result = result["run_result"]

        if use_diff:
            if not test.expected == [ s.rstrip() for s in process_result[1] ]:
                result["diff"] = False
                if html_diff:
                    diff = difflib.HtmlDiff()
                    diffs = list(diff.make_file(test.expected, process_result[1]))

                    with open(self.directory / Path(test.name + ".html"), "w") as f:
                        result["html_file"] = self.directory / Path(test.name + ".html")
                        for line in diffs:
                            f.write(line)
            else:
                result["diff"] = True

        return result
