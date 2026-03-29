from enum import IntEnum, StrEnum
from pathlib import Path

from grader.logger import LogColor

class TestState(StrEnum):
    DIFF_MATCH = "Results match"
    DIFF_MISMATCH = "Results do not match"
    FAILURE = "Test failed"
    INCOMPLETE = "Test incomplete"
    TIMEOUT = "Test timed out"
    NEVER = "Test never ran"

class ProcessState(IntEnum):
    SUCCESS = 0
    FAILURE = 1
    TIMEOUT = 2

class Test:
    def __init__(self, name: str, tests_directory: Path):
        self.name: str = name
        self.path: Path = tests_directory / self.name
        self.command: list[str] = Test._command_from_file(self.path)
        self.expected: list[str] = Test._content_from_file(self.path)

    def __repr__(self) -> str:
        return f"{LogColor.BOLD}{self.name}:{LogColor.RESET} {" ".join(self.command)}"

    @classmethod
    def _command_from_file (cls, location: Path) -> list[str]:
        # Assumes test is written on the first line of the file
        with location.open("r") as testfile:
            return testfile.readline().rstrip().split(" ")

    @classmethod
    def _content_from_file (cls, location: Path) -> list[str]:
        with location.open("r") as testfile:
            next(testfile)
            return testfile.read().rstrip().split("\n")


class Given:
    def __init__(self, name: str, givens_directory: Path):
        self.name = name
        self.path = givens_directory / self.name