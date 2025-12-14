#!/usr/bin/python3

"""
Author    Gavin Ruane
          gjruane@calpoly.edu

Program   Final Project Automated Script
          CSC 453 (Fall 2025)

          Version 1.0
            11 December 2025 @ 10:58:00 PM
            - First release
"""

from pathlib import Path
import tarfile
import zipfile
from zipfile import ZipFile
import subprocess
import shutil
import os
from argparse import ArgumentParser

BLUE = "\x1b[0;34m"
RED = "\x1b[0;31m"
MAGENTA = "\x1b[0;35m"
GREEN = "\x1b[0;32m"
BLACK = "\x1b[0;30m"
BOLD = "\x1b[1m"
RESET = "\x1b[0m"

parser = ArgumentParser(
    prog="grade_final",
    description="Automates the final project grading process",
    epilog="Created by Gavin Ruane"
)
parser.add_argument(
    "-c",
    "--clearvisualizer",
    action="store_true",
    help="Clears visualizer directory upon completion of script if used."
)
args = parser.parse_args()

class MakefileNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ProgramNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

class VisualizerError(Exception):
    def __init__(self, message):
        super().__init__(message)

def main ():
    current_dir = Path(__file__).resolve().parent
    visualizer_env = current_dir / "visualizer_env"
    input_txt = current_dir / "input.txt"

    submissions = current_dir / "submissions"
    if not submissions.exists():
        print_message(f"Directory 'submissions' does not exist. Creating `submissions`", "note")
        submissions.mkdir()

    submissions_zip = current_dir / "submissions.zip"
    if submissions_zip.exists() and len(list(submissions.iterdir())) == 0:
        print_message(f"Unzipping {submissions_zip.name}.", "note")
        unzip_submissions(submissions_zip, submissions)

    outputs = current_dir / "output_files"
    if not outputs.exists():
        print_message("Directory 'output_files' does not exist. Creating 'output_files'...", "note")
        outputs.mkdir()

    for submission in submissions.iterdir():
        extract_submission(submission, outputs)

    for output in sorted(outputs.iterdir(), key=lambda path: path.name):
        print_message(f"Grading {output.name}", "student", pre_newline=True)
        result: str = input(f"Continue grading {output.name}? (Y/n)")
        if result.lower() == "n":
            continue

        print_readme(output)
        
        input("Press enter to run 'make'.")
        try:
            run_make(output)
        except MakefileNotFoundError as e:
            print_message(f"\n{BOLD}Skipping {output.name} due to exception: {e}.{RESET}", "error")
            continue

        input("Press enter to run program and generate step.bin files.")
        try:
            run_program(output, input_txt)
        except Exception as e:
            print_message(f"\n{BOLD}Skipping {output.name} due to exception: {e}.{RESET}", "error")
            continue

        input("Press enter to visualize bin files.")
        try:
            visualize(output, visualizer_env)
        except Exception as e:
            print_message(f"\n{BOLD}Skipping {output.name} due to exception: {e}.{RESET}", "error")
            continue
        
        input("Press enter to continue to next student.")

    if args.clearvisualizer:
        clear_visualizer(visualizer_env)
        
    print_message("All students completed.", "note")

    return

def unzip_submissions (submissions_zip: Path, submissions_dir: Path) -> None:
    if zipfile.is_zipfile(submissions_zip):
        with ZipFile(submissions_zip) as archive:
            archive.extractall(path=submissions_dir)

    return

def extract_submission (submission: Path, outputs: Path) -> None:
    # Create student submission directory
    student = submission.stem.split("_")[0]
    student_dir = outputs / student
    try:
        student_dir.mkdir()
        
        # Extract .tar.gz file
        if tarfile.is_tarfile(submission):
            with tarfile.open(submission, "r:gz") as archive:
                archive.extractall(path=student_dir, filter="tar")
                remove_top_directory(student_dir)
    except:
        print_message(f"Directory '{student_dir.name}' already exists, skipping.", "note")

    return

def remove_top_directory (student_dir: Path) -> None:
    top_level = list(student_dir.iterdir())

    if len(top_level) == 1 and top_level[0].is_dir():
        print_message(f"Restructuring {student_dir.name}'s' submission.", "note")
        directory = top_level[0]

        for file in directory.iterdir():
            shutil.move(str(file), str(student_dir))

        directory.rmdir()

    return

def print_readme (student_dir: Path) -> None:
    readmes = [ readme for readme in student_dir.glob("README*") ]
    if len(readmes) != 0:
        print(f"\n{BOLD}{student_dir.name}'s README{RESET} (path: {readmes[0]})")
        print(readmes[0].read_text())
    else:
        print_message("README not found", "error")

    return

def run_make (student_dir: Path) -> None:
    makefiles = [ file for file in student_dir.iterdir() if file.is_file() and file.name.lower() == "makefile" ]
    if len(makefiles) != 0:
        print(f"\n{BOLD}{student_dir.name}'s Makefile{RESET} (path: {makefiles[0]})")
        try:
            make_result = subprocess.run(["make", "-f", makefiles[0]], cwd=student_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except Exception as e:
            raise MakefileNotFoundError(f"Makefile could not run: exception {e}")

        if make_result.returncode != 0:
            print_message("Make did not run successfully.", "error")
            print(f"\n{BOLD}Make error:{RESET} {make_result.stdout}")
        else:
            print_message("Make ran successfully.", "success")
    else:
        print_message("Makefile not found", "error")
        raise MakefileNotFoundError("Makefile not found.")

    return

def run_program (student_dir: Path, input: Path) -> None:
    programs = [ program for program in student_dir.iterdir() if program.is_file() and os.access(program, os.X_OK) ]
    if len(programs) != 0:
        program = programs[0]
        print(f"\n{BOLD}{student_dir.name}'s program{RESET} (path: {program})")

        student_bins = student_dir / "bins"
        student_bins.mkdir(exist_ok=True)
        program_result = subprocess.run([program, input], cwd=student_bins)

        if program_result.returncode != 0 and len(list(student_bins.iterdir())) == 0:
            print_message(f"{program} did not run successfully; trying 'local' input.txt", "error")
            shutil.copy(input, student_dir)
            program_result = subprocess.run([program], cwd=student_dir)
            
            bins = [ bin for bin in student_dir.iterdir() if bin.is_file() and bin.suffix == ".bin" ]
            for bin in bins:
                shutil.move(bin, student_bins)
            print_message(f"Manually moved {len(bins)} bin files to 'bins' directory.", "note")

            if program_result.returncode != 0:
                print_message(f"{program} did not run successfully.", "error")
        else:
            print_message(f"{program} ran successfully.", "success")
    else:
        print_message("Program not found", "error")
        raise ProgramNotFoundError("Program not found.")

    return

def clear_visualizer (visualizer_env: Path) -> None:
    visualizer_dir = visualizer_env / "visualizer"

    existing_bins = [ bin for bin in visualizer_dir.iterdir() if bin.is_file() and bin.suffix == ".bin" ]
    if len(existing_bins) != 0:
        for bin in existing_bins:
            bin.unlink()
        print_message("Deleted existing bin files in visualizer directory.", "note")

    return
    

def visualize (student_dir: Path, visualizer_env: Path) -> None:
    visualizer_dir = visualizer_env / "visualizer"
    student_bins_dir = student_dir / "bins"

    clear_visualizer(visualizer_env)

    new_bins = [ bin for bin in student_bins_dir.iterdir() if bin.is_file() and bin.suffix == ".bin" ]
    if len(new_bins) != 0:
        number_bins: int = 0
        for bin in new_bins:
            number_bins += 1
            shutil.copy(bin, visualizer_dir)

        print(f"\n{BOLD}{student_dir.name}'s {number_bins} bin files copied{RESET}")

        if number_bins > 0 and visualizer_dir.exists():
            subprocess.run(["./visualizer"], cwd=visualizer_dir, stdout=subprocess.DEVNULL)
    else:
        print_message(f"No bin files in {student_dir.name}'s directory'", "error")

    return
        
        

def print_message (message: str, type: str, pre_newline=False) -> None:
    color = ""
    
    match type.lower():
        case "error":
            color = RED
        case "note" | "info":
            color = BLUE
        case "student":
            color = MAGENTA
        case "success":
            color = GREEN
        case _:
            color = BLACK

    if pre_newline:
        print(f"\n{color}{type}: {RESET}{message}")
    else:
        print(f"{color}{type}: {RESET}{message}")

if __name__ == "__main__":
    main()
