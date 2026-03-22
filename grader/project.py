import tomllib
from collections.abc import Generator
from pathlib import Path

from student import Student

class Project:
    def __init__(self, config_file: str):
        with open(config_file, "rb") as config:
            self.config = tomllib.load(config)

    def __repr__(self) -> str:
        return str(self.config)

    def projects(cls, submissions: Path) -> Generator[object, None, None]:
        for archive in submissions.iterdir():
            yield Student(archive=archive)

newproj = Project("project1.toml")
print(newproj)
