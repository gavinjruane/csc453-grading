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
    action="store_true",
    help="Whether to run the program in interactive mode",
    default=False,
)
parser.add_argument(
    "--timeout",
    type=int,
    help="Timeout for individual program in seconds",
    default=30,
)
parser.add_argument(
    "-c",
    "--check-language",
    action="store_true",
    help="Whether to prompt the grader for the project language"
)
args = parser.parse_args()


def main():
    project = Project(args.file, timeout=args.timeout)
    if args.interactive:
        project.grade(wait_after_step=True, wait_at_end=True, allow_skips=True, print_results=False, check_language=True)
    else:
        project.grade(wait_at_end=True, allow_skips=True, print_results=True, check_language=True)
    print(f"Failures: {project.failures}")
    print(f"Some errors: {project.partials}")
    print(f"Successes: {project.successes}")

    return


if __name__ == "__main__":
    main()
