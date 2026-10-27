# Tests for gui_app.py
#
# Run from the project folder (next to main.py) with:  python3 test_gui_app.py
# The tests open the GUI in the background. The main window is hidden and the
# error window is replaced by a list of messages, except in one test.

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import tkinter as tk

from university_app.src.database.database import Database
from university_app.src.system.student import Student
from university_app.src.system.student_repository import StudentRepository
from university_app.src.system.subject import Subject
from university_app.src.utils.id_generator import IDGenerator
from university_app.src.utils.validator import Validator
from university_app.src.gui import gui_app
from university_app.src.gui.gui_app import (
    AdminPage,
    GUIUniApp,
    LoginPage,
    RegisterPage,
    StudentPage,
    SubjectPage,
    UniversityPage
    )


class GuiTests(unittest.TestCase):

    def setUp(self):
        """Create fresh dependencies and test data for each test."""
        self.temp = TemporaryDirectory(prefix="uniapp-gui-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "students.data"

        self.repo = StudentRepository.createStudentRepository(Database(self.path))
        self.app = GUIUniApp(self.repo, Validator(self.repo), IDGenerator(self.repo))
        self.app.root.withdraw()
        self.addCleanup(self.app.root.destroy)

        # the real error window is only used in one test, the others just record messages
        self.realShowMessage = self.app.showMessage
        self.messages = []
        self.app.showMessage = lambda title, message: self.messages.append((title, message))

        # what the "are you sure" question answers
        self.answer = True
        self.app.askYesNo = lambda title, message: self.answer

    # ---------- helpers ----------

    def reload(self):
        """Load a new repository from the temporary database file."""
        return StudentRepository.createStudentRepository(Database(self.path))

    def addJane(self, marks=()):
        """Save a sample student with subjects for the supplied marks."""
        subjects = [Subject(f"{index:03d}", mark, Subject.calculateGrade(mark))
                    for index, mark in enumerate(marks, 1)]
        self.repo.addStudent(Student(
            "000007", "Jane Smith", "jane.smith@university.com", "Hello123", subjects
        ))

    def pressLogin(self, email, password):
        """Populate the login fields and invoke the login action."""
        self.app.showLoginWindow()
        page = self.app.pages[LoginPage]
        page.email.set(email)
        page.password.set(password)
        page.safe(page.onLoginPressed)()

    def loginAsJane(self):
        """Log in as the sample student and return the subject page."""
        self.pressLogin("jane.smith@university.com", "Hello123")
        return self.app.pages[SubjectPage]

    def tableIds(self, page):
        """Return the subject IDs displayed in the table."""
        return [page.table.set(item, "id") for item in page.table.get_children()]

    def adminText(self):
        """Return the text displayed in the admin output area."""
        return self.app.pages[AdminPage].output.get("1.0", "end")

    def readGroups(self, text):
        # turns the admin text into {"Z": [entries], "P": [entries], ...}
        """Parse displayed admin groups into a dictionary of entries."""
        groups = {}
        current = None
        for line in text.splitlines()[1:]:
            if line.startswith("        "):
                groups[current].append(line.strip())
            elif line.strip():
                current = line.split()[0]
                groups[current] = []
        return groups

    # ---------- pages ----------

    def testThereIsOnePageForEachController(self):
        """Verify there is one page for each controller."""
        self.assertEqual(set(self.app.pages), {
            UniversityPage, AdminPage, StudentPage, LoginPage, RegisterPage, SubjectPage
        })

    def testShowPageRemembersTheCurrentPage(self):
        """Verify show page remembers the current page."""
        for pageClass in (AdminPage, StudentPage, RegisterPage, UniversityPage):
            self.app.showPage(pageClass)
            self.assertEqual(self.app.currentPage, pageClass)

        self.app.showLoginWindow()
        self.assertEqual(self.app.currentPage, LoginPage)

    # ---------- login page ----------

    def testIsAnyFieldEmpty(self):
        """Verify is any field empty."""
        page = self.app.pages[LoginPage]
        self.assertTrue(page.isAnyFieldEmpty("", "Hello123"))
        self.assertTrue(page.isAnyFieldEmpty("jane.smith@university.com", ""))
        self.assertTrue(page.isAnyFieldEmpty("   ", "Hello123"))
        self.assertTrue(page.isAnyFieldEmpty("", ""))
        self.assertFalse(page.isAnyFieldEmpty("jane.smith@university.com", "Hello123"))

    def testIsEmailFormatValid(self):
        """Verify is email format valid."""
        page = self.app.pages[LoginPage]
        self.assertTrue(page.isEmailFormatValid("jane.smith@university.com"))
        for bad in ["invalid", "jane@university.com", "jane.smith@gmail.com", ""]:
            self.assertFalse(page.isEmailFormatValid(bad), bad)

    def testFindStudentReturnsTheMatchOrNone(self):
        """Verify find student returns the match or none."""
        self.addJane()
        page = self.app.pages[LoginPage]
        self.assertEqual(page.findStudent("jane.smith@university.com", "Hello123").student_id, "000007")
        self.assertIsNone(page.findStudent("jane.smith@university.com", "Wrong123"))
        self.assertIsNone(page.findStudent("john.smith@university.com", "Hello123"))

    def testLoginWithEmptyFieldsShowsError(self):
        """Verify login with empty fields shows error."""
        self.pressLogin("", "")
        self.assertEqual(self.messages, [("Error", "Email and password cannot be empty")])
        self.assertEqual(self.app.currentPage, LoginPage)

    def testEmptyCheckComesBeforeEmailFormatCheck(self):
        """Verify empty check comes before email format check."""
        self.pressLogin("invalid", "")
        self.assertEqual(self.messages, [("Error", "Email and password cannot be empty")])

    def testLoginWithBadEmailFormatShowsError(self):
        """Verify login with bad email format shows error."""
        self.addJane()
        self.pressLogin("invalid", "Hello123")
        self.assertEqual(self.messages, [("Error", gui_app.EMAIL_HELP)])
        self.assertEqual(self.app.currentPage, LoginPage)

    def testLoginWithWrongPasswordOrUnknownEmailShowsError(self):
        """Verify login with wrong password or unknown email shows error."""
        self.addJane()
        self.pressLogin("jane.smith@university.com", "Wrong123")
        self.pressLogin("john.smith@university.com", "Hello123")
        self.assertEqual(self.messages, [("Error", "Student does not exist")] * 2)
        self.assertEqual(self.app.currentPage, LoginPage)

    def testGoodLoginOpensTheSubjectPage(self):
        """Verify good login opens the subject page."""
        self.addJane([55, 85])
        self.loginAsJane()

        self.assertEqual(self.messages, [])
        self.assertEqual(self.app.currentPage, SubjectPage)
        self.assertEqual(self.app.currentStudent.student_id, "000007")
        self.assertIn("Jane Smith", self.app.pages[SubjectPage].welcome.get())

    def testLoginFieldsAreClearedWhenThePageIsShownAgain(self):
        """Verify login fields are cleared when the page is shown again."""
        self.pressLogin("jane.smith@university.com", "Hello123")
        self.app.showLoginWindow()
        page = self.app.pages[LoginPage]
        self.assertEqual((page.email.get(), page.password.get()), ("", ""))

    # ---------- register page ----------

    def register(self, email, password, name):
        """Populate the registration form and invoke the register action."""
        self.app.showPage(RegisterPage)
        page = self.app.pages[RegisterPage]
        page.email.set(email)
        page.password.set(password)
        page.name.set(name)
        page.safe(page.onRegisterPressed)()

    def testRegisterSavesTheStudentAndGoesBack(self):
        """Verify register saves the student and goes back."""
        self.register("jane.smith@university.com", "Hello123", "Jane Smith")

        saved = self.reload().getStudents()
        self.assertEqual(len(saved), 1)
        self.assertEqual((saved[0].name, saved[0].email), ("Jane Smith", "jane.smith@university.com"))
        self.assertEqual(saved[0].getSubjects(), [])
        self.assertEqual(self.messages[0][0], "Registered")
        self.assertEqual(self.app.currentPage, StudentPage)

    def testRegisteredStudentCanLogIn(self):
        """Verify registered student can log in."""
        self.register("jane.smith@university.com", "Hello123", "Jane Smith")
        self.pressLogin("jane.smith@university.com", "Hello123")
        self.assertEqual(self.app.currentPage, SubjectPage)

    def testRegisterRejectsDuplicateEmail(self):
        """Verify register rejects duplicate email."""
        self.addJane()
        self.register("jane.smith@university.com", "Hello123", "Someone Else")

        self.assertEqual(self.messages, [("Error", "Student Jane Smith already exists")])
        self.assertEqual(len(self.reload().getStudents()), 1)

    def testRegisterRejectsBadInputAndSavesNothing(self):
        """Verify register rejects bad input and saves nothing."""
        self.register("invalid", "Hello123", "Jane Smith")
        self.register("jane.smith@university.com", "hello123", "Jane Smith")
        self.register("jane.smith@university.com", "Hello123", "   ")
        self.register("", "", "")

        self.assertEqual([message for title, message in self.messages], [
            gui_app.EMAIL_HELP,
            gui_app.PASSWORD_HELP,
            "Email, password and name cannot be empty",
            "Email, password and name cannot be empty",
        ])
        self.assertEqual(self.reload().getStudents(), [])

    # ---------- subject page ----------

    def testSubjectTableListsIdMarkAndGrade(self):
        """Verify subject table lists id mark and grade."""
        self.addJane([55, 85])
        page = self.loginAsJane()

        rows = [page.table.set(item) for item in page.table.get_children()]
        self.assertEqual(len(rows), 2)
        self.assertEqual([str(row["id"]) for row in rows], ["001", "002"])
        self.assertEqual([str(row["mark"]) for row in rows], ["55", "85"])
        self.assertEqual([row["grade"] for row in rows], ["P", "HD"])
        self.assertIn("2 out of 4", page.welcome.get())

    def testFourSubjectLimitAndFifthIsRefused(self):
        """Verify four subject limit and fifth is refused."""
        self.addJane()
        page = self.loginAsJane()

        with patch.object(Subject, "generateSubjectMark", return_value=65):
            for _ in range(5):
                page.safe(page.onEnrolPressed)()

        subjects = self.reload().getStudent("000007").getSubjects()
        self.assertEqual(len(subjects), 4)
        self.assertEqual(len({subject.subject_id for subject in subjects}), 4)
        self.assertTrue(all(s.mark == 65 and s.grade == "C" for s in subjects))
        self.assertEqual(len(page.table.get_children()), 4)
        self.assertEqual(self.messages, [("Error", "Students are allowed to enrol in 4 subjects only")])
        self.assertIn("4 out of 4", page.welcome.get())

    def testFailedSaveShowsErrorAndKeepsTheFile(self):
        """Verify failed save shows error and keeps the file."""
        self.addJane()
        page = self.loginAsJane()
        before = self.path.read_bytes()

        with patch.object(self.repo, "updateStudent", side_effect=OSError("Cannot save")):
            page.safe(page.onEnrolPressed)()

        self.assertEqual(self.messages, [("Error", "Cannot save")])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(page.table.get_children(), ())

    def testRemoveSelectedSubjectFreesAPlace(self):
        """Verify remove selected subject frees aplace."""
        self.addJane([55, 65, 75, 85])
        page = self.loginAsJane()

        page.table.selection_set("001")
        page.safe(page.onRemovePressed)()

        saved = self.reload().getStudent("000007").getSubjects()
        self.assertEqual(sorted(subject.subject_id for subject in saved), ["002", "003", "004"])
        self.assertEqual(len(page.table.get_children()), 3)

        page.safe(page.onEnrolPressed)()
        self.assertEqual(len(self.reload().getStudent("000007").getSubjects()), 4)
        self.assertEqual(self.messages, [])

    def testRemoveWithoutSelectingShowsError(self):
        """Verify remove without selecting shows error."""
        self.addJane([55])
        page = self.loginAsJane()

        page.safe(page.onRemovePressed)()

        self.assertEqual(self.messages, [("Error", "Select a subject in the table first")])
        self.assertEqual(len(self.reload().getStudent("000007").getSubjects()), 1)

    def testChangePasswordIsSaved(self):
        """Verify change password is saved."""
        self.addJane()
        page = self.loginAsJane()
        page.newPassword.set("World456")
        page.confirmPassword.set("World456")

        page.safe(page.onChangePasswordPressed)()

        validator = Validator(self.reload())
        self.assertEqual(validator.login("jane.smith@university.com", "World456").student_id, "000007")
        with self.assertRaises(ValueError):
            validator.login("jane.smith@university.com", "Hello123")
        self.assertEqual(self.messages, [])

    def testChangePasswordMismatchOrBadFormatKeepsTheOldPassword(self):
        """Verify change password mismatch or bad format keeps the old password."""
        self.addJane()
        page = self.loginAsJane()

        page.newPassword.set("World456")
        page.confirmPassword.set("Wrong123")
        page.safe(page.onChangePasswordPressed)()

        page.newPassword.set("bad")
        page.confirmPassword.set("bad")
        page.safe(page.onChangePasswordPressed)()

        self.assertEqual([message for title, message in self.messages],
                         ["Password does not match - try again", gui_app.PASSWORD_HELP])
        self.assertEqual(self.reload().getStudent("000007").password, "Hello123")

    def testLogoutGoesBackToTheStudentPage(self):
        """Verify logout goes back to the student page."""
        self.addJane()
        page = self.loginAsJane()

        page.onLogoutPressed()

        self.assertIsNone(self.app.currentStudent)
        self.assertEqual(self.app.currentPage, StudentPage)

    # ---------- admin page ----------

    def testShowStudents(self):
        """Verify show students."""
        page = self.app.pages[AdminPage]
        page.safe(page.showStudents)()
        self.assertIn("< Nothing to Display >", self.adminText())

        self.addJane()
        page.safe(page.showStudents)()
        self.assertIn("Jane Smith :: 000007 --> Email: jane.smith@university.com", self.adminText())

    def testGroupByGradeUsesTheUnroundedAverage(self):
        """Verify group by grade uses the unrounded average."""
        cases = [
            ([49, 50, 50, 50], "Z"), ([50, 50, 50, 50], "P"),
            ([64, 65, 65, 65], "P"), ([65, 65, 65, 65], "C"),
            ([74, 75, 75, 75], "C"), ([75, 75, 75, 75], "D"),
            ([84, 85, 85, 85], "D"), ([85, 85, 85, 85], "HD"),
        ]
        for number, (marks, grade) in enumerate(cases, 1):
            subjects = [Subject(f"{number * 10 + i:03d}", mark, Subject.calculateGrade(mark))
                        for i, mark in enumerate(marks)]
            self.repo.addStudent(Student(f"{number:06d}", f"Boundary {chr(64 + number)}", f"boundary.{chr(96 + number)}@university.com",
                                         "Hello123", subjects))

        page = self.app.pages[AdminPage]
        page.safe(page.groupStudents)()
        groups = self.readGroups(self.adminText())

        for number, (marks, grade) in enumerate(cases, 1):
            self.assertTrue(any(entry.startswith(f"Boundary {chr(64 + number)} ::") for entry in groups[grade]),
                            f"Boundary {number} should be in {grade}")

    def testPassFailPartitionUsesTheUnroundedAverage(self):
        """Verify pass fail partition uses the unrounded average."""
        cases = [([49, 50, 50, 50], "FAIL"), ([50, 50, 50, 50], "PASS"), ([85, 85, 85, 85], "PASS")]
        for number, (marks, status) in enumerate(cases, 1):
            subjects = [Subject(f"{number * 10 + i:03d}", mark, Subject.calculateGrade(mark))
                        for i, mark in enumerate(marks)]
            self.repo.addStudent(Student(f"{number:06d}", f"Boundary {chr(64 + number)}", f"boundary.{chr(96 + number)}@university.com",
                                         "Hello123", subjects))

        page = self.app.pages[AdminPage]
        page.safe(page.partitionStudents)()
        groups = self.readGroups(self.adminText())

        for number, (marks, status) in enumerate(cases, 1):
            self.assertTrue(any(entry.startswith(f"Boundary {chr(64 + number)} ::") for entry in groups[status]))
        self.assertNotIn("UNCLASSIFIED", groups)

    def testStudentWithNoSubjectsIsUngradedAndUnclassified(self):
        """Verify student with no subjects is ungraded and unclassified."""
        self.addJane()
        page = self.app.pages[AdminPage]

        page.safe(page.groupStudents)()
        self.assertIn("UNGRADED (1)", self.adminText())
        page.safe(page.partitionStudents)()
        self.assertIn("UNCLASSIFIED (1)", self.adminText())

    def testGroupAndPartitionOnAnEmptyDatabase(self):
        """Verify group and partition on an empty database."""
        page = self.app.pages[AdminPage]

        page.safe(page.groupStudents)()
        self.assertIn("< Nothing to Display >", self.adminText())

        page.safe(page.partitionStudents)()
        self.assertIn("FAIL (0)", self.adminText())
        self.assertIn("PASS (0)", self.adminText())

    def testRemoveStudentChecksTheIdAndSavesTheRemoval(self):
        """Verify remove student checks the id and saves the removal."""
        self.addJane()
        page = self.app.pages[AdminPage]

        for entered in ["abc", "0", "1000000", "000008"]:
            page.removeId.set(entered)
            page.safe(page.removeStudent)()
        self.assertEqual([message for title, message in self.messages], [
            "Student ID must be a number.",
            "Student ID must be between 000001 and 999999.",
            "Student ID must be between 000001 and 999999.",
            "Student 000008 does not exist",
        ])
        self.assertEqual(len(self.reload().getStudents()), 1)

        page.removeId.set("000007")
        page.safe(page.removeStudent)()
        self.assertIn("Removing Student 000007 Account", self.adminText())
        self.assertEqual(self.reload().getStudents(), [])

    def testClearDatabaseNeedsAYes(self):
        """Verify clear database needs ayes."""
        self.addJane()
        page = self.app.pages[AdminPage]
        before = self.path.read_bytes()

        self.answer = False
        page.safe(page.clearStudents)()
        self.assertEqual(self.path.read_bytes(), before)

        self.answer = True
        page.safe(page.clearStudents)()
        self.assertIn("Students data cleared", self.adminText())
        self.assertEqual(self.reload().getStudents(), [])

    # ---------- error window ----------

    def testErrorIsShownInASeparateSmallWindow(self):
        """Verify error is shown in aseparate small window."""
        self.realShowMessage("Error", "Something went wrong")

        windows = [w for w in self.app.root.winfo_children() if isinstance(w, tk.Toplevel)]
        self.assertEqual(len(windows), 1)
        texts = [w.cget("text") for w in windows[0].winfo_children() if isinstance(w, tk.Label) or w.winfo_class() == "TLabel"]
        self.assertIn("Something went wrong", texts)

        windows[0].destroy()


if __name__ == "__main__":
    unittest.main()