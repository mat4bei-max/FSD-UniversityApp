# University Controller - the main menu of the University System


class UniversityController:

    MENU_PROMPT = "University System: (A)dmin, (S)tudent, or X : "
    EXIT_MESSAGE = "Thank You"

    OPTION_ADMIN = "A"
    OPTION_STUDENT = "S"
    OPTION_EXIT = "X"

    def __init__(self, adminController, studentController):
        self.adminController = adminController
        self.studentController = studentController
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            choice = self.readChoice()
            self.handleChoice(choice)
        print(self.EXIT_MESSAGE)

    def readChoice(self):
        return input(self.MENU_PROMPT)

    def handleChoice(self, choice):
        choice = choice.strip().upper()

        if choice == self.OPTION_ADMIN:
            self.openAdminSystem()
        elif choice == self.OPTION_STUDENT:
            self.openStudentSystem()
        elif choice == self.OPTION_EXIT:
            self.running = False
        # anything else just shows the menu again

    def openAdminSystem(self):
        self.adminController.start()

    def openStudentSystem(self):
        self.studentController.start()