from pydantic import BaseModel

"""
configuration.py

Defines the Pydantic schema for project TOML files.
"""

class MakeConfig(BaseModel):
    run_make: bool
    use_stdout: bool

class SubmissionsConfig(BaseModel):
    directory: str | None = None
    archive_filename: str
    archive_type: str
    submission_type: str
    program: str | None = None

class OutputsConfig(BaseModel):
    directory: str | None = None

class TestsConfig(BaseModel):
    timeout: int | None = None
    directory: str | None = None
    givens_directory: str | None = None

class Configuration(BaseModel):
    name: str
    root_directory: str | None = None

    make: MakeConfig
    submissions: SubmissionsConfig
    outputs: OutputsConfig | None = None
    tests: TestsConfig | None = None

