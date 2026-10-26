import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from university_app.src.database.database import Database
from university_app.src.system.student import Student
from university_app.src.system.student_repository import StudentRepository


class TestRepositoryDatabaseIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database, repository and studentfor testing."""
        self.temp_dir = TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "students.json"
        self.database = Database(self.path)
        self.repo = StudentRepository.createStudentRepository(self.database)
        self.student = Student(
            student_id="100001",
            name="John Doe",
            email="john.doe@university.com",
            password="password",
            subjects=[],
        )

    def test_added_student_can_be_loaded_again(self):
        """Test that a student added to the repository can be loaded again from the database."""
        with TemporaryDirectory() as directory:

            # add the student and then load it again through new instances
            self.repo.addStudent(self.student)
            new_database = Database(self.path)
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
