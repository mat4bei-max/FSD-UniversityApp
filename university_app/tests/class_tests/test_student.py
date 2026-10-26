import unittest

from university_app.src.system.student import Student
from university_app.src.system.subject import Subject
    


class TestSubject(unittest.TestCase):

    def setUp(self):
        """Set up a default student for testing."""
        self.student = Student(
            "100001",
            'John Doe',
            'john.doe@university.com',
            'password',
            subjects=[]
        )

    def test_add_subject_to_student(self):
        """Test adding a subject to the student."""
        subject = Subject("200001", 80, 'D')
        self.student.addSubject(subject)

        self.assertEqual(len(self.student.subjects), 1)
        self.assertEqual(self.student.subjects[0].subject_id, "200001")
        self.assertEqual(self.student.subjects[0].mark, 80)
        self.assertEqual(self.student.subjects[0].grade, 'D')

    def test_remove_subject_to_student(self):
        """Test removing a subject from the student."""
        subject = Subject("200001", 80, 'D')
        self.student.addSubject(subject)

        with self.assertRaisesRegex(ValueError, f"Subject with ID 100001 not found."):
            self.student.removeSubject("100001")

        self.student.removeSubject("200001")
        self.assertEqual(self.student.getSubjects(), [])

    def test_to_many_subjects_to_student(self):
        """Test that adding too many subjects to a student raises a ValueError."""
        subject1 = Subject("000001", 80, 'D')
        subject2 = Subject("000002", 80, 'D')
        subject3 = Subject("000003", 80, 'D')
        subject4 = Subject("000004", 80, 'D')
        subject5 = Subject("000005", 80, 'D')

        self.student.addSubject(subject1)
        self.student.addSubject(subject2)
        self.student.addSubject(subject3)
        self.student.addSubject(subject4)

        with self.assertRaisesRegex(ValueError, r"Maximum number of subjects \(4\) reached\."):
            self.student.addSubject(subject5)

    def test_create_student_with_mismatched_name_raises(self):
        """Test that creating a student with a missmatch between mail and name raises ValueError. """

        with self.assertRaisesRegex(ValueError, "Name does not match the name derived from the email."):
            self.student = Student(
                "100001",
                'Jane Doe',
                'john.doe@university.com',
                'password',
                subjects=[]
            )

if __name__ == '__main__':
    unittest.main()
