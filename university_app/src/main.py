# main.py - starts the University System (CLI version)

from pathlib import Path

from university_app.src.controllers.admin_controller import AdminController
from university_app.src.controllers.student_controller import StudentController
from university_app.src.controllers.university_controller import UniversityController
from university_app.src.database.database import Database
from university_app.src.system.student_repository import StudentRepository
from university_app.src.utils.id_generator import IDGenerator
from university_app.src.utils.validator import Validator


# The path is built from this file's location, so it works from any folder.
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "students.data"

def main():
    """Initialize shared services and run the command-line application."""
    try:
        database = Database(DATA_PATH)
        repo = StudentRepository.createStudentRepository(database)
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        print(f"Could not load the students file: {error}")
        return

    validator = Validator(repo)
    generator = IDGenerator(repo)

    # both controllers get the same repo, so they always see the same students
    # StudentController builds the SubjectController by itself
    admin_controller = AdminController(repo)
    student_controller = StudentController(repo, validator, generator)

    university_controller = UniversityController(admin_controller, student_controller)
    university_controller.run()


if __name__ == "__main__":
    main()
