from pathlib import Path

from university_app.src.database.database import Database
from university_app.src.system.student import Student
from university_app.src.system.student_repository import StudentRepository
from university_app.src.utils.validator import Validator
from university_app.src.utils.id_generator import IDGenerator
from university_app.src.controllers.subject_controller import SubjectController


class StudentController:
    def __init__(self, repo, validator, generator):
        self.repo = repo
        self.validator = validator
        self.generator = generator

    def run(self):
        while True:
            choice = input(
                "    Student System (l/r/x): "
            ).strip().lower()

            try:
                if choice == "l":
                    self.login()

                elif choice == "r":
                    self.register()

                elif choice == "x":
                    return

                else:
                    print("    Invalid choice. Enter l, r, or x.")

            except (ValueError, OSError) as error:
                print(f"    {error}")

    def read_credentials(self):
        while True:
            email = input("    Email: ").strip()
            password = input("    Password: ")
            try:
                self.validator.validateEmail(email)
                self.validator.validatePassword(password)
            except ValueError:
                print("    Incorrect email or password format")
                continue
            print("    email and password formats acceptable")
            return email, password

    def register(self):
        print("    Student Sign Up")

        email, password = self.read_credentials()
        try:
            self.validator.ensureNewEmail(email)
        except ValueError:
            existing = next(
                (student for student in self.repo.getStudents()
                 if student.email == email), None
            )
            if existing is not None:
                raise ValueError(f"Student {existing.name} already exists") from None
            raise

        name = input("    Name: ").strip()
        if not name:
            raise ValueError("Name cannot be empty.")

        student_id = self.generator.generateStudentId()

        student = Student(
            student_id,
            name,
            email,
            password,
            []
        )

        self.repo.addStudent(student)

        print(f"    Enrolling Student {name}")

    def login(self):
        print("    Student Sign In")

        email, password = self.read_credentials()
        try:
            student = self.validator.login(email, password)
        except ValueError:
            raise ValueError("Student does not exist") from None

        subject_controller = SubjectController(
            self.repo,
            self.validator,
            self.generator
        )

        subject_controller.run(student.student_id)

        return student


if __name__ == "__main__":
    data_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "students.data"
    )

    database = Database(data_path)
    repo = StudentRepository.createStudentRepository(database)
    validator = Validator(repo)
    generator = IDGenerator(repo)

    controller = StudentController(repo, validator, generator)
    controller.run()
