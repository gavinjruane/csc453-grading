from pathlib import Path


class Test:
    def __init__(self, name: str, tests_directory: Path):
        self.name = name
        self.path = tests_directory / self.name
        self.command = Test._command_from_file(self.path)

        print(self.command)

    @classmethod
    def _command_from_file (cls, location: Path):
        # Assumes test is written on the first line of the file
        with location.open("r") as testfile:
            return testfile.readline().rstrip().split(" ")