from exceptions import *
from config import *

from pathlib import Path

class Test:
    tests_directory: Path = Path()
    
    def __init__ (self, location: Path):
        self.location: Path = location
        self.command: list[str] = Test._command_from_file(self.location)

    def __repr__ (self):
        return f"Location: {str(self.location)}, Command: {self.command}"

    @classmethod
    def _command_from_file (cls, location: Path):
        # Assumes test is written on the first line of the file
        with location.open("r") as testfile:
            return testfile.readline().rstrip().split(" ")

    @classmethod
    def list_from_directory (cls, tests: Path | None = None) -> list["Test"]:
        if tests is None:
            tests = Test.tests_directory

        return [ cls(test) for test in tests.iterdir() if test.is_file() ]

