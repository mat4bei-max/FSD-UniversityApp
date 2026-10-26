import unittest

from university_app.src.system.subject import Subject
    


class TestSubject(unittest.TestCase):

    def setUp(self):
        """Set up a default subject for testing."""
        self.subject = Subject(
            subject_id="001",
            mark=80,
            grade='D',
        )

    def test_subject_creation(self):
        """Test that the subject is created correctly."""
        self.assertEqual(self.subject.subject_id, "001")
        self.assertEqual(self.subject.mark, 80)
        self.assertEqual(self.subject.grade, 'D')

    def test_create_subject_with_invalid_mark(self):
        """Test that creating a subject with an invalid mark raises ValueError."""
        with self.assertRaisesRegex(ValueError, "Invalid mark: 20"):
            Subject(
                subject_id="002",
                mark=20,
                grade='Z'
            )

    def test_create_subject_with_invalid_grade(self):
        """Test that creating a subject with an invalid grade raises ValueError."""
        with self.assertRaisesRegex(ValueError, "Invalid grade: P for mark: 80"):
            Subject(
                subject_id="003",
                mark=80,
                grade='P'
            )
   
if __name__ == '__main__':
    unittest.main()
