import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from university_app.src.database.database import Database
from university_app.src.system.student import Student
from university_app.src.system.student_repository import StudentRepository


class TestRepositoryDatabaseIntegration(unittest.TestCase):

    def test_added_student_can_be_loaded_again(self):
        """Test that a student added to the repository can be loaded again from the database."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "students.json"

            # Initialize the database and repository
            database = Database(path)
            repo = StudentRepository.createStudentRepository(database)
            student = Student(
                student_id="100001",
                name="John Doe",
                email="john.doe@university.com",
                password="password",
                subjects=[],
            )

            # add the student and then load it again through new instances
            repo.addStudent(student)
            new_database = Database(path)
            new_repo = StudentRepository.createStudentRepository(new_database)

            # Test that the student was correctly loaded from the new repository instance
            self.assertEqual(len(new_repo.getStudents()), 1)

            loaded_student = new_repo.getStudent("100001")
            self.assertEqual(loaded_student.name, "John Doe")
            self.assertEqual(
                loaded_student.email,
                "john.doe@university.com",
            )


if __name__ == '__main__':
    unittest.main()
