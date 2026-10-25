# Tests for UniversityController
# Run with:  python test.py

import unittest
from unittest.mock import MagicMock, patch

from university_controller import UniversityController


class TestUniversityController(unittest.TestCase):

    def setUp(self):
        # MagicMock objects pretend to be the admin and student controllers
        self.admin = MagicMock()
        self.student = MagicMock()
        self.controller = UniversityController(self.admin, self.student)

    def testConstructorStoresControllers(self):
        self.assertIs(self.controller.adminController, self.admin)
        self.assertIs(self.controller.studentController, self.student)

    def testReadChoiceReturnsWhatUserTyped(self):
        with patch("builtins.input", return_value="A") as mockInput:
            choice = self.controller.readChoice()

        self.assertEqual(choice, "A")
        mockInput.assert_called_with(UniversityController.MENU_PROMPT)

    def testAdminOption(self):
        self.controller.handleChoice("A")

        self.admin.start.assert_called_once()
        self.student.start.assert_not_called()

    def testStudentOption(self):
        self.controller.handleChoice("S")

        self.student.start.assert_called_once()
        self.admin.start.assert_not_called()

    def testExitOptionStopsTheLoop(self):
        self.controller.running = True
        self.controller.handleChoice("X")

        self.assertFalse(self.controller.running)

    def testLowercaseAndSpacesWork(self):
        self.controller.handleChoice(" a ")
        self.controller.handleChoice("s")

        self.admin.start.assert_called_once()
        self.student.start.assert_called_once()

    def testWrongInputDoesNothing(self):
        self.controller.running = True
        self.controller.handleChoice("Z")
        self.controller.handleChoice("")

        self.admin.start.assert_not_called()
        self.student.start.assert_not_called()
        self.assertTrue(self.controller.running)

    def testRunPrintsExitMessage(self):
        with patch("builtins.input", side_effect=["X"]):
            with patch("builtins.print") as mockPrint:
                self.controller.run()

        mockPrint.assert_called_with(UniversityController.EXIT_MESSAGE)

    def testFullSequence(self):
        # the real controllers ask for "x" to exit
        self.admin.start.side_effect = lambda: input("x to exit: ")
        self.student.start.side_effect = lambda: input("x to exit: ")

        with patch("builtins.input", side_effect=["A", "x", "S", "x", "X"]) as mockInput:
            with patch("builtins.print") as mockPrint:
                self.controller.run()

        self.admin.start.assert_called_once()
        self.student.start.assert_called_once()
        self.assertEqual(mockInput.call_count, 5)
        mockPrint.assert_called_with(UniversityController.EXIT_MESSAGE)


if __name__ == "__main__":
    unittest.main()