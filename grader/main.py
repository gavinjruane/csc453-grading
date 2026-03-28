from argparse import ArgumentParser

from grader.project import Project

parser = ArgumentParser(
    prog="grader",
    description="Automated CSC 453 grader",
    epilog="Created by Gavin Ruane"
)
parser.add_argument(
    "-v",
    "--version",
    action="version",
    version="%(prog)s 1.0",
    help="Display application version",
)
parser.add_argument(
    "-f",
    "--file",
    type=str,
    required=True,
    help="The project configuration file to use (.toml format)",
)
parser.add_argument(
    "-i",
    "--interactive",
    type=bool,
    help="Whether to run the program in interactive mode",
    default=False,
)
args = parser.parse_args()


def main():
    project = Project(args.file)
    if args.interactive:
        failures, some_errors, successes = project.grade(wait_after_step=True, wait_at_end=True, allow_skips=True)
    else:
        failures, some_errors, successes = project.grade()
    print(f"Failures: {failures}")
    print(f"Some errors: {some_errors}")
    print(f"Successes: {successes}")

    return


if __name__ == "__main__":
    main()
