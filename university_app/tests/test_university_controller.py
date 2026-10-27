# Tests for UniversityController
# Run with:  python test.py

import unittest
from unittest.mock import MagicMock, patch

from university_app.src.controllers.university_controller import UniversityController


class TestUniversityController(unittest.TestCase):

    def setUp(self):
        """Create fresh dependencies and test data for each test."""
        self.admin = MagicMock(spec=["run"])
        self.student = MagicMock(spec=["run"])
        self.controller = UniversityController(self.admin, self.student)

    # runs the menu with typed answers, nothing is really printed
    def runWith(self, answers):
        """Run the university menu with simulated input and capture its calls."""
        with patch("builtins.input", side_effect=answers) as mockInput:
            with patch("builtins.print") as mockPrint:
                self.controller.run()
        return mockInput, mockPrint

    # ---------- constants and constructor ----------

    def testConstants(self):
        # real text on purpose, so wrong wording is caught
        """Verify constants."""
        self.assertEqual(UniversityController.MENU_PROMPT,
                         "University System: (A)dmin, (S)tudent, or X : ")
        self.assertEqual(UniversityController.EXIT_MESSAGE, "Thank You")
        self.assertEqual(UniversityController.OPTION_ADMIN, "A")
        self.assertEqual(UniversityController.OPTION_STUDENT, "S")
        self.assertEqual(UniversityController.OPTION_EXIT, "X")

    def testConstructor(self):
        """Verify constructor."""
        self.assertIs(self.controller.adminController, self.admin)
        self.assertIs(self.controller.studentController, self.student)
        self.assertFalse(self.controller.running)

    # ---------- readChoice ----------

    def testReadChoiceReturnsRawText(self):
        """Verify read choice returns raw text."""
        with patch("builtins.input", return_value=" a ") as mockInput:
            choice = self.controller.readChoice()

        self.assertEqual(choice, " a ")
        mockInput.assert_called_once_with(UniversityController.MENU_PROMPT)

    # ---------- handleChoice ----------

    def testAdminOption(self):
        """Verify admin option."""
        self.controller.handleChoice("A")

        self.admin.run.assert_called_once()
        self.student.run.assert_not_called()

    def testStudentOption(self):
        """Verify student option."""
        self.controller.handleChoice("S")

        self.student.run.assert_called_once()
        self.admin.run.assert_not_called()

    def testExitOption(self):
        """Verify exit option."""
        self.controller.running = True
        self.controller.handleChoice("X")

        self.assertFalse(self.controller.running)
        self.admin.run.assert_not_called()
        self.student.run.assert_not_called()

    def testLowercaseAndSpacesWork(self):
        """Verify lowercase and spaces work."""
        for choice in ["a", " a ", " A", "\tA\n"]:
            self.controller.handleChoice(choice)
        self.assertEqual(self.admin.run.call_count, 4)

        for choice in ["s", " S "]:
            self.controller.handleChoice(choice)
        self.assertEqual(self.student.run.call_count, 2)

    def testLowercaseExit(self):
        """Verify lowercase exit."""
        self.controller.running = True
        self.controller.handleChoice(" x ")

        self.assertFalse(self.controller.running)

    def testWrongInputDoesNothing(self):
        """Verify wrong input does nothing."""
        self.controller.running = True

        # whole words and extra letters are not allowed, only the single letter
        for choice in ["Z", "", "   ", "1", "AS", "SA", "XA", "AA", "A S",
                       "Apple", "admin", "student", "exit"]:
            self.controller.handleChoice(choice)

        self.admin.run.assert_not_called()
        self.student.run.assert_not_called()
        self.assertTrue(self.controller.running)

    # ---------- run ----------

    def testExitRightAway(self):
        """Verify exit right away."""
        mockInput, mockPrint = self.runWith(["X"])

        self.admin.run.assert_not_called()
        self.student.run.assert_not_called()
        mockPrint.assert_called_once_with("Thank You")

    def testWrongInputShowsMenuAgain(self):
        """Verify wrong input shows menu again."""
        mockInput, mockPrint = self.runWith(["Z", "", "AS", "X"])

        self.assertEqual(mockInput.call_count, 4)
        self.admin.run.assert_not_called()
        self.student.run.assert_not_called()
        mockPrint.assert_called_once_with("Thank You")

    def testMenuComesBackAfterSubSystem(self):
        """Verify menu comes back after sub system."""
        mockInput, mockPrint = self.runWith(["A", "A", "S", "X"])

        self.assertEqual(self.admin.run.call_count, 2)
        self.assertEqual(self.student.run.call_count, 1)
        self.assertEqual(mockInput.call_count, 4)

    def testRunCanBeUsedTwice(self):
        """Verify run can be used twice."""
        self.runWith(["X"])
        mockInput, mockPrint = self.runWith(["S", "X"])

        self.student.run.assert_called_once()
        self.assertEqual(mockInput.call_count, 2)
        mockPrint.assert_called_once_with("Thank You")

    def testFullSequence(self):
        # keeps the order of everything that happens
        """Verify full sequence."""
        events = []

        # the real controllers wait for "x", so the fake ones do too
        def adminRun():
            """Record an admin visit and simulate waiting for an exit choice."""
            events.append("admin")
            input("x to exit: ")

        def studentRun():
            """Record a student visit and simulate waiting for an exit choice."""
            events.append("student")
            input("x to exit: ")

        self.admin.run.side_effect = adminRun
        self.student.run.side_effect = studentRun

        with patch("builtins.input", side_effect=["A", "x", "S", "x", "X"]) as mockInput:
            with patch("builtins.print", side_effect=events.append):
                self.controller.run()

        # Thank You must come last and only once
        self.assertEqual(events, ["admin", "student", "Thank You"])
        self.assertEqual(mockInput.call_count, 5)


if __name__ == "__main__":
    unittest.main()