from pathlib import Path


class Test:
    def __init__(self, name: str, tests_directory: Path):
        self.name = name
        self.path = tests_directory / self.name