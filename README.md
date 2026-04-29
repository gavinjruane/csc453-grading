# csc453-grading

A grading program for Cal Poly CSC 453 created by **Gavin Ruane**.

## Installation

Grader is in a development state right now, so its installation process is not elegant.

1. Clone this repository to your local machine.

    `git clone git@github.com:gavinjruane/csc453-grading.git`
2. Navigate to the newly-created directory.

    `cd csc453-grading`
3. Create a Python virtual environment for the program.

    `python -m venv .venv`
4. Activate the virtual environment in your shell session.

    `. .venv/bin/activate`
5. Install the necessary third-party libraries.

    `pip install -r requirements.txt`
6. 

## Basic Usage

To run Grader, you must specify a project file (see [Projects](#Projects)) at the minimum.
You can also specify other options to change the Grader experience.

| Argument              | Description                                        |
|-----------------------|----------------------------------------------------|
| `-h`, `--help`        | Show a help message                                |
| `-v`, `--version`     | Display version information for Grader             |
| `-f`, `--file FILE`   | Project configuration file to use (in TOML format) |
| `-i`, `--interactive` | Whether to run the program in interactive mode     |
| `--timeout TIMEOUT`   | Timeout for individual programs in seconds         |

### Interactive mode

By default, Grader runs in a *semi-interactive* mode.

## Projects

To avoid a massive list of command-line arguments for each grading session, Grader uses `.toml` files that set up an
environment specific to each project. Each TOML file must conform to a schema to be used for grading.

## Tests

Tests are formatted as **plain-text** files. As of right now, tests fall into two categories:

- *Diff:* These tests provide a command that the student program should run as well as the expected output. Grader will
    use the expected output to run an HTML diff with the student's output.
- *Timing:* These tests simply provide a command that the student program should run. They rely on manual grader
    inspection and therefore do not use diff or any other automation tool.

### Test file format

Test files must follow the following format, as Grader uses this format to extract the relevant information from them.

```
./<student-program> <arguments>
[<test-type>]
<expected-output>
```

For example:

```
./schedule 1000 two 1
[diff]
    1
```