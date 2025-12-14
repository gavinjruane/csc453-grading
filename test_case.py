from student import Student
from test import Test
from pathlib import Path

def unzip_submissions (submissions_zip: Path, submissions_dir: Path) -> None:
    if zipfile.is_zipfile(submissions_zip):
        with ZipFile(submissions_zip) as archive:
            archive.extractall(path=submissions_dir)

    return


Student.students_directory = Path.cwd() / "output_files"
print(Student.students_directory)
Student.students_directory.mkdir(exist_ok=True)

Test.tests_directory = Path.cwd() / "tests"
print(Test.tests_directory)
print(Test.list_from_directory())

# for student in sorted(Student.iter_from_directory(Path.cwd() / "submissions"), key=lambda student: student.name):
#     print(student.name + ": " + str(student.archive))
#     student.extract()
#     student.readme()
#     input("MAKE")
#     try:
#         student.make()
#     except Exception as e:
#         input(f"SKIP, due to {e}")
#         continue
#     input("RUN")
#     try:
#         student.run(look_for="tinyFSDemo")
#     except Exception as e:
#         input(f"SKIP, due to {e}")
#         continue
#     input("Wait...")

