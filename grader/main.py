from argparse import ArgumentParser

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
    help="The project configuration file to use (.toml format)",
)
args = parser.parse_args()

def main():
    input("hello")
    return

if __name__ == "__main__":
    main()
