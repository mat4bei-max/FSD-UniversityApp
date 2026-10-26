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

import gui_app
from gui_app import (AdminPage, GUIUniApp, LoginPage, RegisterPage,
                     StudentPage, SubjectPage, UniversityPage)
from university_app.src.database.database import Database
from university_app.src.system.student import Student
from university_app.src.system.student_repository import StudentRepository
from university_app.src.system.subject import Subject
from university_app.src.utils.id_generator import IDGenerator
from university_app.src.utils.validator import Validator


class GuiTests(unittest.TestCase):

    def setUp(self):
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
        return StudentRepository.createStudentRepository(Database(self.path))

    def addJane(self, marks=()):
        subjects = [Subject(index, mark, Subject.calculateGrade(mark))
                    for index, mark in enumerate(marks, 1)]
        self.repo.addStudent(Student(
            7, "Jane Smith", "jane.smith@university.com", "Hello123", subjects
        ))

    def pressLogin(self, email, password):
        self.app.showLoginWindow()
        page = self.app.pages[LoginPage]
        page.email.set(email)
        page.password.set(password)
        page.safe(page.onLoginPressed)()

    def loginAsJane(self):
        self.pressLogin("jane.smith@university.com", "Hello123")
        return self.app.pages[SubjectPage]

    def tableIds(self, page):
        return [page.table.set(item, "id") for item in page.table.get_children()]

    def adminText(self):
        return self.app.pages[AdminPage].output.get("1.0", "end")

    def readGroups(self, text):
        # turns the admin text into {"Z": [entries], "P": [entries], ...}
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
        self.assertEqual(set(self.app.pages), {
            UniversityPage, AdminPage, StudentPage, LoginPage, RegisterPage, SubjectPage
        })

    def testShowPageRemembersTheCurrentPage(self):
        for pageClass in (AdminPage, StudentPage, RegisterPage, UniversityPage):
            self.app.showPage(pageClass)
            self.assertEqual(self.app.currentPage, pageClass)

        self.app.showLoginWindow()
        self.assertEqual(self.app.currentPage, LoginPage)

    # ---------- login page ----------

    def testIsAnyFieldEmpty(self):
        page = self.app.pages[LoginPage]
        self.assertTrue(page.isAnyFieldEmpty("", "Hello123"))
        self.assertTrue(page.isAnyFieldEmpty("jane.smith@university.com", ""))
        self.assertTrue(page.isAnyFieldEmpty("   ", "Hello123"))
        self.assertTrue(page.isAnyFieldEmpty("", ""))
        self.assertFalse(page.isAnyFieldEmpty("jane.smith@university.com", "Hello123"))

    def testIsEmailFormatValid(self):
        page = self.app.pages[LoginPage]
        self.assertTrue(page.isEmailFormatValid("jane.smith@university.com"))
        for bad in ["invalid", "jane@university.com", "jane.smith@gmail.com", ""]:
            self.assertFalse(page.isEmailFormatValid(bad), bad)

    def testFindStudentReturnsTheMatchOrNone(self):
        self.addJane()
        page = self.app.pages[LoginPage]
        self.assertEqual(page.findStudent("jane.smith@university.com", "Hello123").student_id, 7)
        self.assertIsNone(page.findStudent("jane.smith@university.com", "Wrong123"))
        self.assertIsNone(page.findStudent("john.smith@university.com", "Hello123"))

    def testLoginWithEmptyFieldsShowsError(self):
        self.pressLogin("", "")
        self.assertEqual(self.messages, [("Error", "Email and password cannot be empty")])
        self.assertEqual(self.app.currentPage, LoginPage)

    def testEmptyCheckComesBeforeEmailFormatCheck(self):
        self.pressLogin("invalid", "")
        self.assertEqual(self.messages, [("Error", "Email and password cannot be empty")])

    def testLoginWithBadEmailFormatShowsError(self):
        self.addJane()
        self.pressLogin("invalid", "Hello123")
        self.assertEqual(self.messages, [("Error", gui_app.EMAIL_HELP)])
        self.assertEqual(self.app.currentPage, LoginPage)

    def testLoginWithWrongPasswordOrUnknownEmailShowsError(self):
        self.addJane()
        self.pressLogin("jane.smith@university.com", "Wrong123")
        self.pressLogin("john.smith@university.com", "Hello123")
        self.assertEqual(self.messages, [("Error", "Student does not exist")] * 2)
        self.assertEqual(self.app.currentPage, LoginPage)

    def testGoodLoginOpensTheSubjectPage(self):
        self.addJane([55, 85])
        self.loginAsJane()

        self.assertEqual(self.messages, [])
        self.assertEqual(self.app.currentPage, SubjectPage)
        self.assertEqual(self.app.currentStudent.student_id, 7)
        self.assertIn("Jane Smith", self.app.pages[SubjectPage].welcome.get())

    def testLoginFieldsAreClearedWhenThePageIsShownAgain(self):
        self.pressLogin("jane.smith@university.com", "Hello123")
        self.app.showLoginWindow()
        page = self.app.pages[LoginPage]
        self.assertEqual((page.email.get(), page.password.get()), ("", ""))

    # ---------- register page ----------

    def register(self, email, password, name):
        self.app.showPage(RegisterPage)
        page = self.app.pages[RegisterPage]
        page.email.set(email)
        page.password.set(password)
        page.name.set(name)
        page.safe(page.onRegisterPressed)()

    def testRegisterSavesTheStudentAndGoesBack(self):
        self.register("jane.smith@university.com", "Hello123", "Jane Smith")

        saved = self.reload().getStudents()
        self.assertEqual(len(saved), 1)
        self.assertEqual((saved[0].name, saved[0].email), ("Jane Smith", "jane.smith@university.com"))
        self.assertEqual(saved[0].getSubjects(), [])
        self.assertEqual(self.messages[0][0], "Registered")
        self.assertEqual(self.app.currentPage, StudentPage)

    def testRegisteredStudentCanLogIn(self):
        self.register("jane.smith@university.com", "Hello123", "Jane Smith")
        self.pressLogin("jane.smith@university.com", "Hello123")
        self.assertEqual(self.app.currentPage, SubjectPage)

    def testRegisterRejectsDuplicateEmail(self):
        self.addJane()
        self.register("jane.smith@university.com", "Hello123", "Someone Else")

        self.assertEqual(self.messages, [("Error", "Student Jane Smith already exists")])
        self.assertEqual(len(self.reload().getStudents()), 1)

    def testRegisterRejectsBadInputAndSavesNothing(self):
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
        self.addJane([55, 85])
        page = self.loginAsJane()

        rows = [page.table.set(item) for item in page.table.get_children()]
        self.assertEqual(len(rows), 2)
        self.assertEqual([str(row["id"]) for row in rows], ["001", "002"])
        self.assertEqual([str(row["mark"]) for row in rows], ["55", "85"])
        self.assertEqual([row["grade"] for row in rows], ["P", "HD"])
        self.assertIn("2 out of 4", page.welcome.get())

    def testFourSubjectLimitAndFifthIsRefused(self):
        self.addJane()
        page = self.loginAsJane()

        with patch.object(Subject, "generateSubjectMark", return_value=65):
            for _ in range(5):
                page.safe(page.onEnrolPressed)()

        subjects = self.reload().getStudent(7).getSubjects()
        self.assertEqual(len(subjects), 4)
        self.assertEqual(len({subject.subject_id for subject in subjects}), 4)
        self.assertTrue(all(s.mark == 65 and s.grade == "C" for s in subjects))
        self.assertEqual(len(page.table.get_children()), 4)
        self.assertEqual(self.messages, [("Error", "Students are allowed to enrol in 4 subjects only")])
        self.assertIn("4 out of 4", page.welcome.get())

    def testFailedSaveShowsErrorAndKeepsTheFile(self):
        self.addJane()
        page = self.loginAsJane()
        before = self.path.read_bytes()

        with patch.object(self.repo, "updateStudent", side_effect=OSError("Cannot save")):
            page.safe(page.onEnrolPressed)()

        self.assertEqual(self.messages, [("Error", "Cannot save")])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(page.table.get_children(), ())

    def testRemoveSelectedSubjectFreesAPlace(self):
        self.addJane([55, 65, 75, 85])
        page = self.loginAsJane()

        page.table.selection_set("1")
        page.safe(page.onRemovePressed)()

        saved = self.reload().getStudent(7).getSubjects()
        self.assertEqual(sorted(subject.subject_id for subject in saved), [2, 3, 4])
        self.assertEqual(len(page.table.get_children()), 3)

        page.safe(page.onEnrolPressed)()
        self.assertEqual(len(self.reload().getStudent(7).getSubjects()), 4)
        self.assertEqual(self.messages, [])

    def testRemoveWithoutSelectingShowsError(self):
        self.addJane([55])
        page = self.loginAsJane()

        page.safe(page.onRemovePressed)()

        self.assertEqual(self.messages, [("Error", "Select a subject in the table first")])
        self.assertEqual(len(self.reload().getStudent(7).getSubjects()), 1)

    def testChangePasswordIsSaved(self):
        self.addJane()
        page = self.loginAsJane()
        page.newPassword.set("World456")
        page.confirmPassword.set("World456")

        page.safe(page.onChangePasswordPressed)()

        validator = Validator(self.reload())
        self.assertEqual(validator.login("jane.smith@university.com", "World456").student_id, 7)
        with self.assertRaises(ValueError):
            validator.login("jane.smith@university.com", "Hello123")
        self.assertEqual(self.messages, [])

    def testChangePasswordMismatchOrBadFormatKeepsTheOldPassword(self):
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
        self.assertEqual(self.reload().getStudent(7).password, "Hello123")

    def testLogoutGoesBackToTheStudentPage(self):
        self.addJane()
        page = self.loginAsJane()

        page.onLogoutPressed()

        self.assertIsNone(self.app.currentStudent)
        self.assertEqual(self.app.currentPage, StudentPage)

    # ---------- admin page ----------

    def testShowStudents(self):
        page = self.app.pages[AdminPage]
        page.safe(page.showStudents)()
        self.assertIn("< Nothing to Display >", self.adminText())

        self.addJane()
        page.safe(page.showStudents)()
        self.assertIn("Jane Smith :: 000007 --> Email: jane.smith@university.com", self.adminText())

    def testGroupByGradeUsesTheUnroundedAverage(self):
        cases = [
            ([49, 50, 50, 50], "Z"), ([50, 50, 50, 50], "P"),
            ([64, 65, 65, 65], "P"), ([65, 65, 65, 65], "C"),
            ([74, 75, 75, 75], "C"), ([75, 75, 75, 75], "D"),
            ([84, 85, 85, 85], "D"), ([85, 85, 85, 85], "HD"),
        ]
        for number, (marks, grade) in enumerate(cases, 1):
            subjects = [Subject(number * 10 + i, mark, Subject.calculateGrade(mark))
                        for i, mark in enumerate(marks)]
            self.repo.addStudent(Student(number, f"Boundary {number}", "fixture@example.com",
                                         "Hello123", subjects))

        page = self.app.pages[AdminPage]
        page.safe(page.groupStudents)()
        groups = self.readGroups(self.adminText())

        for number, (marks, grade) in enumerate(cases, 1):
            self.assertTrue(any(entry.startswith(f"Boundary {number} ::") for entry in groups[grade]),
                            f"Boundary {number} should be in {grade}")

    def testPassFailPartitionUsesTheUnroundedAverage(self):
        cases = [([49, 50, 50, 50], "FAIL"), ([50, 50, 50, 50], "PASS"), ([85, 85, 85, 85], "PASS")]
        for number, (marks, status) in enumerate(cases, 1):
            subjects = [Subject(number * 10 + i, mark, Subject.calculateGrade(mark))
                        for i, mark in enumerate(marks)]
            self.repo.addStudent(Student(number, f"Boundary {number}", "fixture@example.com",
                                         "Hello123", subjects))

        page = self.app.pages[AdminPage]
        page.safe(page.partitionStudents)()
        groups = self.readGroups(self.adminText())

        for number, (marks, status) in enumerate(cases, 1):
            self.assertTrue(any(entry.startswith(f"Boundary {number} ::") for entry in groups[status]))
        self.assertNotIn("UNCLASSIFIED", groups)

    def testStudentWithNoSubjectsIsUngradedAndUnclassified(self):
        self.addJane()
        page = self.app.pages[AdminPage]

        page.safe(page.groupStudents)()
        self.assertIn("UNGRADED (1)", self.adminText())
        page.safe(page.partitionStudents)()
        self.assertIn("UNCLASSIFIED (1)", self.adminText())

    def testGroupAndPartitionOnAnEmptyDatabase(self):
        page = self.app.pages[AdminPage]

        page.safe(page.groupStudents)()
        self.assertIn("< Nothing to Display >", self.adminText())

        page.safe(page.partitionStudents)()
        self.assertIn("FAIL (0)", self.adminText())
        self.assertIn("PASS (0)", self.adminText())

    def testRemoveStudentChecksTheIdAndSavesTheRemoval(self):
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
        self.realShowMessage("Error", "Something went wrong")

        windows = [w for w in self.app.root.winfo_children() if isinstance(w, tk.Toplevel)]
        self.assertEqual(len(windows), 1)
        texts = [w.cget("text") for w in windows[0].winfo_children() if isinstance(w, tk.Label) or w.winfo_class() == "TLabel"]
        self.assertIn("Something went wrong", texts)

        windows[0].destroy()


if __name__ == "__main__":
    unittest.main()