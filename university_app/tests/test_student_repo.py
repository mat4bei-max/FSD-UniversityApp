import unittest
from unittest.mock import Mock

from university_app.src.database.database import Database
from university_app.src.system.student import Student
from university_app.src.system.student_repository import StudentRepository
from university_app.src.system.subject import Subject


class TestStudentRepository(unittest.TestCase):

    def setUp(self):
        """Set up a mock database and a student repository with an empty list of students."""
        self.database = Mock(spec=Database)
        self.database.load.return_value = []
        self.repo = StudentRepository.createStudentRepository(self.database)
        self.student = Student(
            "100001",
            'John Doe',
            'john.doe@university.com',
            'password',
            subjects=[]
        )

    def test_create_repository_loads_existing_students(self):
        """Test that creating a repository loads existing students from the database."""
        self.database.load.reset_mock()
        self.database.load.return_value = [self.student]

        repo = StudentRepository.createStudentRepository(self.database)

        self.database.load.assert_called_once_with()
        self.assertEqual(len(repo.getStudents()), 1)
        self.assertEqual(repo.getStudent("100001").email, self.student.email)
        self.database.save.assert_not_called()

    def test_create_repository_with_empty_database(self):
        """Test that creating a repository with an empty database results in an empty repository."""
        self.assertEqual(self.repo.getStudents(), [])
        self.database.load.assert_called_once_with()
        self.database.save.assert_not_called()

    def test_add_student(self):
        """Test adding a student to the repository."""
        self.repo.addStudent(self.student)

        self.assertEqual(len(self.repo.getStudents()), 1)
        saved = self.repo.getStudent("100001")
        self.assertEqual(saved.name, 'John Doe')
        self.assertEqual(saved.email, 'john.doe@university.com')
        self.assertEqual(saved.subjects, [])
        self.database.save.assert_called_once()
        saved_students = self.database.save.call_args.args[0]
        self.assertEqual(len(saved_students), 1)
        saved_student = saved_students[0]
        self.assertIsNot(saved_student, self.student)
        self.assertEqual(saved_student.student_id, self.student.student_id)
        self.assertEqual(saved_student.name, self.student.name)
        self.assertEqual(saved_student.email, self.student.email)
        self.assertEqual(saved_student.password, self.student.password)
        self.assertEqual(saved_student.subjects, [])

    def test_add_student_with_subject(self):
        """Test adding a student with a subject to the repository."""
        self.student.addSubject(Subject("200001", 80, 'D'))

        self.repo.addStudent(self.student)

        saved = self.repo.getStudent("100001")
        self.assertEqual(len(self.repo.getStudents()), 1)
        self.assertEqual(len(saved.subjects), 1)
        self.assertEqual(saved.subjects[0].subject_id, "200001")
        self.assertEqual(saved.subjects[0].mark, 80)
        self.assertEqual(saved.subjects[0].grade, 'D')
        self.database.save.assert_called_once()
        saved_students = self.database.save.call_args.args[0]
        self.assertEqual(len(saved_students), 1)
        saved_student = saved_students[0]
        self.assertIsNot(saved_student, self.student)
        self.assertEqual(saved_student.student_id, self.student.student_id)
        self.assertEqual(saved_student.name, self.student.name)
        self.assertEqual(saved_student.email, self.student.email)
        self.assertEqual(saved_student.password, self.student.password)
        self.assertEqual(len(saved_student.subjects), 1)
        saved_subject = saved_student.subjects[0]
        self.assertIsNot(saved_subject, self.student.subjects[0])
        self.assertEqual(saved_subject.subject_id, "200001")
        self.assertEqual(saved_subject.mark, 80)
        self.assertEqual(saved_subject.grade, 'D')

    def test_get_unknown_student_raises(self):
        """Test that attempting to get an unknown student raises a ValueError."""
        with self.assertRaisesRegex(ValueError, 'Student with ID 999999 not found'):
            self.repo.getStudent("999999")

    def test_get_student_returns_independent_copy(self):
        """Test that getting a student returns an independent copy."""
        self.repo.addStudent(self.student)

        retrieved = self.repo.getStudent("100001")
        retrieved.name = 'Changed'

        self.assertEqual(self.repo.getStudent("100001").name, 'John Doe')

if __name__ == '__main__':
    unittest.main()
