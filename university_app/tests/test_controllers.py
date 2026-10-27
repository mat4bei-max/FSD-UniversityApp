"""Integration checks using the team's classes and temporary database files."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from university_app.src.controllers.admin_controller import AdminController
from university_app.src.controllers.student_controller import StudentController
from university_app.src.controllers.subject_controller import SubjectController
from university_app.src.database.database import Database
from university_app.src.system.student import Student
from university_app.src.system.student_repository import StudentRepository
from university_app.src.system.subject import Subject
from university_app.src.utils.id_generator import IDGenerator
from university_app.src.utils.validator import Validator


class ControllerTests(unittest.TestCase):
    def setUp(self):
        """Create fresh dependencies and test data for each test."""
        self.temp = TemporaryDirectory(prefix="uniapp-test-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "students.data"
        self.repo = StudentRepository.createStudentRepository(Database(self.path))
        self.validator = Validator(self.repo)
        self.generator = IDGenerator(self.repo)
        self.student = StudentController(self.repo, self.validator, self.generator)
        self.subject = SubjectController(self.repo, self.validator, self.generator)
        self.admin = AdminController(self.repo)
        self.prompts = []

    def run_menu(self, controller, answers, *args):
        """Run a controller with simulated input and capture its output."""
        answers = iter(answers)
        output = StringIO()

        def read(prompt):
            """Record the input prompt and return the next simulated answer."""
            self.prompts.append(prompt)
            return next(answers)

        with patch("builtins.input", side_effect=read), redirect_stdout(output):
            controller.run(*args)
        return output.getvalue()

    def reload(self):
        """Load a new repository from the temporary database file."""
        return StudentRepository.createStudentRepository(Database(self.path))

    def add_jane(self, marks=()):
        """Save a sample student with subjects for the supplied marks."""
        subjects = [Subject(f"{index:03d}", mark, Subject.calculateGrade(mark))
                    for index, mark in enumerate(marks, 1)]
        self.repo.addStudent(Student(
            "000007", "Jane Smith", "jane.smith@university.com", "Hello123", subjects
        ))

    def test_registration_is_saved_and_duplicate_is_rejected(self):
        """Verify registration is saved and duplicate is rejected."""
        output = self.run_menu(self.student, [
            "r", "jane.smith@university.com", "Hello123", "Jane Smith",
            "r", "jane.smith@university.com", "Hello123", "x"
        ])
        students = self.reload().getStudents()
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].name, "Jane Smith")
        self.assertIn("    Enrolling Student Jane Smith", output)
        self.assertIn("Student Jane Smith already exists", output)
        self.assertEqual(self.prompts[0], "    Student System (l/r/x): ")

    def test_invalid_formats_retry_credentials_before_registration(self):
        """Verify invalid formats retry credentials before registration."""
        output = self.run_menu(self.student, [
            "r", "invalid", "Hello123",
            "jane.smith@university.com", "hello123",
            "jane.smith@university.com", "Hello123", "Jane Smith", "x"
        ])
        self.assertEqual(output.count("Incorrect email or password format"), 2)
        self.assertEqual(len(self.reload().getStudents()), 1)

    def test_bad_login_recovers_and_good_login_opens_subject_menu(self):
        """Verify bad login recovers and good login opens subject menu."""
        self.add_jane()
        output = self.run_menu(self.student, [
            "l", "jane.smith@university.com", "Wrong123",
            "l", "jane.smith@university.com", "Hello123", "s", "x", "x"
        ])
        self.assertIn("Student does not exist", output)
        self.assertIn("        Showing 0 subjects", output)
        self.assertIn("        Student Course Menu (c/e/r/s/x): ", self.prompts)

    def test_four_subject_limit_preserves_saved_marks_and_ids(self):
        """Verify four subject limit preserves saved marks and ids."""
        self.add_jane()
        with patch.object(Subject, "generateSubjectMark", return_value=65):
            output = self.run_menu(self.subject, ["e", "e", "e", "e", "e", "s", "x"], "000007")
        subjects = self.reload().getStudent("000007").getSubjects()
        self.assertEqual(len(subjects), 4)
        self.assertEqual(len({subject.subject_id for subject in subjects}), 4)
        self.assertTrue(all(subject.mark == 65 and subject.grade == "C" for subject in subjects))
        self.assertIn("Students are allowed to enrol in 4 subjects only", output)

    def test_subject_removal_handles_bad_ids_and_frees_a_place(self):
        """Verify subject removal handles bad ids and frees a place."""
        self.add_jane([55, 65, 75, 85])
        output = self.run_menu(self.subject, [
            "r", "abc", "r", "999", "r", "001", "e", "s", "x"
        ], "000007")
        saved = self.reload().getStudent("000007").getSubjects()
        self.assertEqual(len(saved), 4)
        self.assertIn("Subject ID must be a number", output)
        self.assertIn("Subject with ID 999 not found", output)
        self.assertIn("        Dropping Subject-001", output)
        self.assertEqual(next(subject.mark for subject in saved if subject.subject_id == "002"), 65)

    def test_password_confirmation_change_and_reuse_persist(self):
        """Verify password confirmation change and reuse persist."""
        self.add_jane()
        output = self.run_menu(self.subject, [
            "c", "World456", "Wrong123", "World456",
            "c", "World456", "World456", "x"
        ], "000007")
        validator = Validator(self.reload())
        self.assertEqual(validator.login("jane.smith@university.com", "World456").student_id, "000007")
        with self.assertRaises(ValueError):
            validator.login("jane.smith@university.com", "Hello123")
        self.assertIn("Password does not match - try again", output)

    def test_invalid_new_password_does_not_replace_saved_password(self):
        """Verify invalid new password does not replace saved password."""
        self.add_jane()
        self.run_menu(self.subject, ["c", "bad", "x"], "000007")
        self.assertEqual(self.reload().getStudent("000007").password, "Hello123")

    def test_admin_grades_use_unrounded_student_averages(self):
        """Verify admin grades use unrounded student averages."""
        cases = [
            ([49, 50, 50, 50], "Z", "FAIL"),
            ([50, 50, 50, 50], "P", "PASS"),
            ([64, 65, 65, 65], "P", "PASS"),
            ([65, 65, 65, 65], "C", "PASS"),
            ([74, 75, 75, 75], "C", "PASS"),
            ([75, 75, 75, 75], "D", "PASS"),
            ([84, 85, 85, 85], "D", "PASS"),
            ([85, 85, 85, 85], "HD", "PASS"),
        ]
        for student_id, (marks, grade, status) in enumerate(cases, 1):
            subjects = [Subject(f"{student_id * 10 + i:03d}", mark, Subject.calculateGrade(mark))
                        for i, mark in enumerate(marks)]
            self.repo.addStudent(Student(f"{student_id:06d}", "Boundary " + chr(64 + student_id),
                                         f"boundary.{chr(96 + student_id)}@university.com", "Hello123", subjects))
        output = self.run_menu(self.admin, ["g", "p", "x"])
        lines = output.splitlines()
        for student_id, (marks, grade, status) in enumerate(cases, 1):
            token = "Boundary {} :: {:06d}".format(chr(64 + student_id), student_id)
            self.assertTrue(any(line.startswith("    " + grade + " -->") and token in line
                                for line in lines))
            self.assertTrue(any(line.startswith("    " + status + " -->") and token in line
                                for line in lines))

    def test_empty_database_and_zero_subjects_have_defined_output(self):
        """Verify empty database and zero subjects have defined output."""
        output = self.run_menu(self.admin, ["s", "g", "p", "x"])
        self.assertIn("< Nothing to Display >", output)
        self.assertIn("PASS --> []", output)
        self.add_jane()
        output = self.run_menu(self.admin, ["g", "p", "x"])
        self.assertIn("UNGRADED --> [Jane Smith", output)
        self.assertIn("UNCLASSIFIED --> [Jane Smith", output)

    def test_admin_removal_validates_ids_and_persists_deletion(self):
        """Verify admin removal validates ids and persists deletion."""
        self.add_jane()
        output = self.run_menu(self.admin, ["r", "abc", "r", "000008", "r", "000007", "x"])
        self.assertIn("Student ID must be a number", output)
        self.assertIn("Student 000008 does not exist", output)
        self.assertEqual(self.reload().getStudents(), [])
        self.assertEqual(self.prompts[0], "    Admin System (c/g/p/r/s/x): ")

    def test_clear_requires_confirmation_and_preserves_file_on_cancel(self):
        """Verify clear requires confirmation and preserves file on cancel."""
        self.add_jane()
        snapshot = self.path.read_bytes()
        self.run_menu(self.admin, ["c", "n", "c", "maybe", "x"])
        self.assertEqual(self.path.read_bytes(), snapshot)
        output = self.run_menu(self.admin, ["c", "y", "x"])
        self.assertIn("Students data cleared", output)
        self.assertEqual(self.reload().getStudents(), [])

    def test_write_error_does_not_print_enrolment_success(self):
        """Verify write error does not print enrolment success."""
        self.add_jane()
        snapshot = self.path.read_bytes()
        with patch.object(self.repo, "updateStudent", side_effect=OSError("Cannot save")):
            output = self.run_menu(self.subject, ["e", "x"], "000007")
        self.assertIn("Cannot save", output)
        self.assertNotIn("Enrolling in Subject", output)
        self.assertEqual(self.path.read_bytes(), snapshot)

    def test_unknown_menu_options_recover(self):
        """Verify unknown menu options recover."""
        self.add_jane()
        for controller, args in [(self.student, ()), (self.admin, ()), (self.subject, ("000007",))]:
            output = self.run_menu(controller, ["?", "X"], *args)
            self.assertIn("Invalid choice", output)


if __name__ == "__main__":
    unittest.main()
