import tomllib

from pydantic import BaseModel

class MakeConfig(BaseModel):
    run_make: bool
    use_stdout: bool

class SubmissionsConfig(BaseModel):
    archive_filename: str
    archive_type: str
    package_type: str

class OutputsConfig(BaseModel):
    directory: str

class TestsConfig(BaseModel):
    test_directory: str

class Configuration(BaseModel):
    name: str
    make: MakeConfig
    submissions: SubmissionsConfig
    outputs: OutputsConfig
    tests: TestsConfig


with open("project1.toml", "rb") as config:
    file = tomllib.load(config)
    rt = Configuration.model_validate(file)

    print(rt.make.run_make)

