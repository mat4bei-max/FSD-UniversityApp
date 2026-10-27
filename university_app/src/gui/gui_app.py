# gui_app.py - GUI version of the University System (tkinter)
#
# One window, and one page for each part of the CLI:
#   UniversityPage - like UniversityController (Admin / Student / Exit)
#   AdminPage      - like AdminController      (show, group, partition, remove, clear)
#   StudentPage    - like StudentController    (login or register)
#   LoginPage      - the login window
#   RegisterPage   - the register part of StudentController
#   SubjectPage    - like SubjectController    (enrol, remove, show subjects, change password)
#
# The CLI controllers use input() and print(), so the GUI does not call them.
# It uses the repository, validator and generator directly (see Shiva's notes).
#
# ASSUMPTION: this file sits in the project folder next to main.py and is
# started with:  python3 gui_app.py
# REPLACE LATER if the file is moved (the imports below would change).

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# ASSUMPTION: the GUI uses the same data file as the CLI, taken from main.py
# so both always match. REPLACE LATER if the team keeps the path somewhere else.
from university_app.src.database.database import Database
from university_app.src.system.student import Student
from university_app.src.system.student_repository import StudentRepository
from university_app.src.system.subject import Subject
from university_app.src.utils.id_generator import IDGenerator
from university_app.src.utils.validator import Validator

# ASSUMPTION: the limit is 4 subjects (from the brief). Student.addSubject
# also checks it, this one only gives a nicer message before anything is saved.
MAX_SUBJECTS = 4

EMAIL_HELP = "Email must look like firstname.lastname@university.com"
PASSWORD_HELP = (
    "Password must start with a capital letter, have at least five letters "
    "and then three or more digits (for example Abcde123)"
)
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "students.data"

class Page(ttk.Frame):
    """One screen of the app. Every page reaches the shared objects through self.app."""

    def __init__(self, parent, app):
        """Initialize the instance and its dependencies."""
        super().__init__(parent, padding=20)
        self.app = app
        self.buildPage()

    def buildPage(self):
        """Build the widgets and layout for this page."""
        raise NotImplementedError

    def onShow(self):
        # called every time the page is shown, pages change this when they need a refresh
        """Prepare or refresh the page when it becomes visible."""
        pass

    def addTitle(self, text):
        """Add a heading label to the page."""
        ttk.Label(self, text=text, font=("Helvetica", 20, "bold")).pack(pady=(0, 15))

    def addField(self, form, row, label, variable, hidden=False):
        """Add a labeled input field and return its entry widget."""
        ttk.Label(form, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=5)
        entry = ttk.Entry(form, textvariable=variable, width=32, show="*" if hidden else "")
        entry.grid(row=row, column=1, pady=5)
        return entry

    def safe(self, action):
        # same idea as the CLI controllers: ValueError / OSError become an error message
        """Wrap an action so expected errors appear in a message window."""
        def runAction():
            """Run the wrapped action and display expected errors."""
            try:
                action()
            except (ValueError, OSError) as error:
                self.app.showException(str(error))
        return runAction


class UniversityPage(Page):
    """Main page, like UniversityController: Admin, Student or Exit."""

    def buildPage(self):
        """Build the widgets and layout for this page."""
        self.addTitle("University System")
        ttk.Label(self, text="Who is using the system?").pack(pady=(0, 15))
        ttk.Button(self, text="Admin (no login)", width=25,
                   command=lambda: self.app.showPage(AdminPage)).pack(pady=5)
        ttk.Button(self, text="Student", width=25,
                   command=lambda: self.app.showPage(StudentPage)).pack(pady=5)
        ttk.Button(self, text="Exit", width=25,
                   command=self.app.exitApp).pack(pady=5)


class AdminPage(Page):
    """Like AdminController: show, group, partition, remove and clear students."""

    def buildPage(self):
        """Build the widgets and layout for this page."""
        self.addTitle("Admin System")

        ttk.Button(self, text="Back",
                   command=lambda: self.app.showPage(UniversityPage)).pack(side="bottom", anchor="e", pady=(10, 0))

        buttons = ttk.Frame(self)
        buttons.pack(fill="x")
        for text, action in (("Show Students", self.showStudents),
                             ("Group by Grade", self.groupStudents),
                             ("Pass / Fail", self.partitionStudents),
                             ("Clear Database", self.clearStudents)):
            ttk.Button(buttons, text=text, command=self.safe(action)).pack(side="left", padx=3)

        removeRow = ttk.Frame(self)
        removeRow.pack(fill="x", pady=10)
        self.removeId = tk.StringVar()
        ttk.Label(removeRow, text="Remove student by ID:").pack(side="left")
        ttk.Entry(removeRow, textvariable=self.removeId, width=10).pack(side="left", padx=5)
        ttk.Button(removeRow, text="Remove", command=self.safe(self.removeStudent)).pack(side="left")

        outputFrame = ttk.Frame(self)
        outputFrame.pack(fill="both", expand=True)
        self.output = tk.Text(outputFrame, height=14, width=70, state="disabled", font="TkFixedFont")
        scrollbar = ttk.Scrollbar(outputFrame, command=self.output.yview)
        self.output.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.output.pack(side="left", fill="both", expand=True)

    def onShow(self):
        """Prepare or refresh the page when it becomes visible."""
        self.removeId.set("")
        self.display(["Choose an action above."])

    def display(self, lines):
        """Replace the admin output with the supplied lines."""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines))
        self.output.configure(state="disabled")

    # Same rule as AdminController.average_mark (average of the subjects the student
    # has now). REPLACE LATER if the team moves this rule into Student.
    def averageMark(self, student):
        """Return the average subject mark, or None when no subjects exist."""
        subjects = student.getSubjects()
        if not subjects:
            return None
        return sum(subject.mark for subject in subjects) / len(subjects)

    def describe(self, student):
        """Format a student summary with the average mark and grade."""
        average = self.averageMark(student)
        if average is None:
            return f"{student.name} :: {student.student_id} -- no subjects"
        grade = Subject.calculateGrade(average)
        return f"{student.name} :: {student.student_id} --> GRADE: {grade} - MARK: {average:.2f}"

    def showStudents(self):
        """Display the current student list in the admin page."""
        students = self.app.repo.getStudents()
        lines = ["Student List"]
        if not students:
            lines.append("    < Nothing to Display >")
        for student in students:
            lines.append(f"    {student.name} :: {student.student_id} --> Email: {student.email}")
        self.display(lines)

    def groupStudents(self):
        """Display students grouped by their average grade."""
        students = self.app.repo.getStudents()
        lines = ["Grade Grouping"]
        if not students:
            lines.append("    < Nothing to Display >")
            self.display(lines)
            return

        groups = {grade: [] for grade in ("Z", "P", "C", "D", "HD", "UNGRADED")}
        for student in students:
            average = self.averageMark(student)
            grade = "UNGRADED" if average is None else Subject.calculateGrade(average)
            groups.setdefault(grade, []).append(self.describe(student))

        for grade, entries in groups.items():
            if entries:
                lines.append(f"    {grade} ({len(entries)})")
                lines.extend(f"        {entry}" for entry in entries)
        self.display(lines)

    def partitionStudents(self):
        """Display students grouped by pass, fail, or unclassified status."""
        lines = ["PASS/FAIL Partition"]
        groups = {"FAIL": [], "PASS": [], "UNCLASSIFIED": []}

        for student in self.app.repo.getStudents():
            average = self.averageMark(student)
            if average is None:
                status = "UNCLASSIFIED"
            elif average >= 50:
                status = "PASS"
            else:
                status = "FAIL"
            groups[status].append(self.describe(student))

        for status, entries in groups.items():
            if status != "UNCLASSIFIED" or entries:
                lines.append(f"    {status} ({len(entries)})")
                lines.extend(f"        {entry}" for entry in entries)
        self.display(lines)

    def removeStudent(self):
        """Validate the entered ID and delete the matching student account."""
        entered_id = self.removeId.get().strip()
        if not entered_id.isascii() or not entered_id.isdigit():
            raise ValueError("Student ID must be a number.")
        if not 1 <= int(entered_id) <= 999999:
            raise ValueError("Student ID must be between 000001 and 999999.")

        student_id = entered_id.zfill(6)
        try:
            self.app.repo.removeStudent(student_id)
        except ValueError:
            raise ValueError(f"Student {student_id} does not exist") from None

        self.removeId.set("")
        self.display([f"Removing Student {student_id} Account"])

    def clearStudents(self):
        """Clear student accounts after the user confirms the action."""
        if self.app.askYesNo("Clear database", "Are you sure you want to clear the database?"):
            self.app.repo.clearAllStudents()
            self.display(["Students data cleared"])


class StudentPage(Page):
    """Like StudentController: choose between login and register."""

    def buildPage(self):
        """Build the widgets and layout for this page."""
        self.addTitle("Student System")
        ttk.Button(self, text="Login", width=25,
                   command=self.app.showLoginWindow).pack(pady=5)
        ttk.Button(self, text="Register", width=25,
                   command=lambda: self.app.showPage(RegisterPage)).pack(pady=5)
        ttk.Button(self, text="Back", width=25,
                   command=lambda: self.app.showPage(UniversityPage)).pack(pady=5)


class LoginPage(Page):
    """The login window: email, password and a login button."""

    def buildPage(self):
        """Build the widgets and layout for this page."""
        self.addTitle("Student Login")

        self.email = tk.StringVar()
        self.password = tk.StringVar()

        form = ttk.Frame(self)
        form.pack(pady=10)
        self.addField(form, 0, "Email", self.email)
        passwordEntry = self.addField(form, 1, "Password", self.password, hidden=True)
        passwordEntry.bind("<Return>", lambda event: self.safe(self.onLoginPressed)())

        buttons = ttk.Frame(self)
        buttons.pack(pady=10)
        ttk.Button(buttons, text="Login", command=self.safe(self.onLoginPressed)).pack(side="left", padx=5)
        ttk.Button(buttons, text="Back",
                   command=lambda: self.app.showPage(StudentPage)).pack(side="left", padx=5)

    def onShow(self):
        """Prepare or refresh the page when it becomes visible."""
        self.email.set("")
        self.password.set("")

    def onLoginPressed(self):
        """Validate login details and open the authenticated student page."""
        email = self.email.get().strip()
        password = self.password.get()

        if self.isAnyFieldEmpty(email, password):
            self.app.showException("Email and password cannot be empty")
            return

        if not self.isEmailFormatValid(email):
            self.app.showException(EMAIL_HELP)
            return

        student = self.findStudent(email, password)
        if student is None:
            self.app.showException("Student does not exist")
            return

        self.app.openSubjectWindow(student)

    def isAnyFieldEmpty(self, email, password):
        """Return whether any supplied credential field is empty."""
        return not email.strip() or not password.strip()

    def isEmailFormatValid(self, email):
        # the Validator raises ValueError, this turns it into True / False
        """Return whether the email matches the required format."""
        try:
            self.app.validator.validateEmail(email)
        except ValueError:
            return False
        return True

    def findStudent(self, email, password):
        # Shiva's Validator.login loops over the repository students and raises
        # ValueError if nothing matches. This returns the student or None.
        """Return the student matching the credentials, or None."""
        try:
            return self.app.validator.login(email, password)
        except ValueError:
            return None


class RegisterPage(Page):
    """The register part of StudentController: email, password and name."""

    def buildPage(self):
        """Build the widgets and layout for this page."""
        self.addTitle("Student Sign Up")

        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.name = tk.StringVar()

        form = ttk.Frame(self)
        form.pack(pady=10)
        self.addField(form, 0, "Email", self.email)
        self.addField(form, 1, "Password", self.password, hidden=True)
        self.addField(form, 2, "Name", self.name)

        ttk.Label(self, text="e.g. jane.smith@university.com  /  Hello123").pack()

        buttons = ttk.Frame(self)
        buttons.pack(pady=10)
        ttk.Button(buttons, text="Register", command=self.safe(self.onRegisterPressed)).pack(side="left", padx=5)
        ttk.Button(buttons, text="Back",
                   command=lambda: self.app.showPage(StudentPage)).pack(side="left", padx=5)

    def onShow(self):
        """Prepare or refresh the page when it becomes visible."""
        self.email.set("")
        self.password.set("")
        self.name.set("")

    def onRegisterPressed(self):
        """Validate registration fields and save a new student account."""
        email = self.email.get().strip()
        password = self.password.get()
        name = self.name.get().strip()

        if not email or not password.strip() or not name:
            raise ValueError("Email, password and name cannot be empty")

        validator = self.app.validator

        try:
            validator.validateEmail(email)
        except ValueError:
            raise ValueError(EMAIL_HELP) from None

        try:
            validator.validatePassword(password)
        except ValueError:
            raise ValueError(PASSWORD_HELP) from None

        try:
            validator.ensureNewEmail(email)
        except ValueError:
            existing = next((student for student in self.app.repo.getStudents()
                             if student.email == email), None)
            if existing is None:
                raise
            raise ValueError(f"Student {existing.name} already exists") from None

        student_id = self.app.generator.generateStudentId()
        self.app.repo.addStudent(Student(student_id, name, email, password, []))

        self.app.showMessage("Registered", f"Student {name} is now enrolled. You can log in.")
        self.app.showPage(StudentPage)


class SubjectPage(Page):
    """Like SubjectController: enrol, remove, show subjects and change password."""

    def buildPage(self):
        """Build the widgets and layout for this page."""
        self.addTitle("Student Course Menu")

        self.welcome = tk.StringVar()
        ttk.Label(self, textvariable=self.welcome).pack()

        self.table = ttk.Treeview(self, columns=("id", "mark", "grade"), show="headings",
                                  height=MAX_SUBJECTS, selectmode="browse")
        for column, heading in (("id", "Subject ID"), ("mark", "Mark"), ("grade", "Grade")):
            self.table.heading(column, text=heading)
            self.table.column(column, width=120, anchor="center")
        self.table.pack(pady=10)

        actions = ttk.Frame(self)
        actions.pack()
        ttk.Button(actions, text="Enrol in a new subject",
                   command=self.safe(self.onEnrolPressed)).pack(side="left", padx=5)
        ttk.Button(actions, text="Remove selected subject",
                   command=self.safe(self.onRemovePressed)).pack(side="left", padx=5)

        passwordBox = ttk.LabelFrame(self, text="Change password", padding=10)
        passwordBox.pack(pady=15)
        self.newPassword = tk.StringVar()
        self.confirmPassword = tk.StringVar()
        self.addField(passwordBox, 0, "New password", self.newPassword, hidden=True)
        self.addField(passwordBox, 1, "Confirm password", self.confirmPassword, hidden=True)
        ttk.Button(passwordBox, text="Change password",
                   command=self.safe(self.onChangePasswordPressed)).grid(row=2, column=1, sticky="e", pady=(5, 0))

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status).pack()

        ttk.Button(self, text="Log out", command=self.onLogoutPressed).pack(side="bottom", anchor="e")

    def onShow(self):
        """Prepare or refresh the page when it becomes visible."""
        self.newPassword.set("")
        self.confirmPassword.set("")
        self.status.set("")
        self.showSubjectWindow(self.app.currentStudent)

    def showSubjectWindow(self, student):
        # always read the student again, so the table shows what is really saved
        """Refresh the student details and enrolled subject table."""
        student = self.app.repo.getStudent(student.student_id)
        subjects = student.getSubjects()

        self.table.delete(*self.table.get_children())
        for subject in subjects:
            self.table.insert("", "end", iid=str(subject.subject_id),
                              values=(f"{subject.subject_id}", subject.mark, subject.grade))

        self.welcome.set(f"{student.name}  -  enrolled in {len(subjects)} out of {MAX_SUBJECTS} subjects")

    def onEnrolPressed(self):
        """Enrol the current student and refresh the subject display."""
        student = self.app.currentStudent
        subject = self.enrolInNewSubject(student)
        self.showSubjectWindow(student)
        self.status.set(f"Enrolling in Subject-{subject.subject_id}")

    def enrolInNewSubject(self, student):
        # Mathis's sequence: get, generate, add, update
        """Create and save a subject enrolment for the supplied student."""
        student = self.app.repo.getStudent(student.student_id)

        if len(student.getSubjects()) >= MAX_SUBJECTS:
            raise ValueError(f"Students are allowed to enrol in {MAX_SUBJECTS} subjects only")

        subject_id = self.app.generator.generateSubjectId()
        mark = Subject.generateSubjectMark()
        grade = Subject.calculateGrade(mark)
        subject = Subject(subject_id=subject_id, mark=mark, grade=grade)

        student.addSubject(subject)
        self.app.repo.updateStudent(student)
        return subject

    def onRemovePressed(self):
        """Remove the selected subject and refresh the student display."""
        selected = self.table.selection()
        if not selected:
            raise ValueError("Select a subject in the table first")
        subject_id = selected[0]

        student = self.app.repo.getStudent(self.app.currentStudent.student_id)
        student.removeSubject(subject_id)
        self.app.repo.updateStudent(student)

        self.showSubjectWindow(student)
        self.status.set(f"Dropping Subject-{subject_id}")

    def onChangePasswordPressed(self):
        """Validate the password confirmation and save the new password."""
        new_password = self.newPassword.get()

        try:
            self.app.validator.validatePassword(new_password)
        except ValueError:
            raise ValueError(PASSWORD_HELP) from None

        if self.confirmPassword.get() != new_password:
            raise ValueError("Password does not match - try again")

        student = self.app.repo.getStudent(self.app.currentStudent.student_id)
        student.changePassword(new_password)
        self.app.repo.updateStudent(student)

        self.newPassword.set("")
        self.confirmPassword.set("")
        self.status.set("Password updated")

    def onLogoutPressed(self):
        """Clear the current student and return to the student page."""
        self.app.currentStudent = None
        self.app.showPage(StudentPage)


class GUIUniApp:
    """The window. Holds the shared objects and moves between the pages."""

    def __init__(self, repo, validator, generator):
        """Initialize the instance and its dependencies."""
        self.repo = repo
        self.validator = validator
        self.generator = generator
        self.currentStudent = None
        self.currentPage = None

        self.root = tk.Tk()
        self.root.title("University System")
        self.root.geometry("760x620")
        self.root.minsize(700, 600)

        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # all pages sit on top of each other, showPage() raises the one we want
        self.pages = {}
        for pageClass in (UniversityPage, AdminPage, StudentPage,
                          LoginPage, RegisterPage, SubjectPage):
            page = pageClass(container, self)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[pageClass] = page

    def run(self):
        """Display the university page and start the GUI event loop."""
        self.showPage(UniversityPage)
        self.root.mainloop()

    def showPage(self, pageClass):
        """Refresh and raise the requested page."""
        page = self.pages[pageClass]
        page.onShow()
        page.tkraise()
        self.currentPage = pageClass

    def showLoginWindow(self):
        """Display the login page."""
        self.showPage(LoginPage)

    def openSubjectWindow(self, student):
        """Set the authenticated student and display the subject page."""
        self.currentStudent = student
        self.showPage(SubjectPage)

    def showException(self, message):
        """Display an error message in a separate window."""
        self.showMessage("Error", message)

    def showMessage(self, title, message):
        # a small separate window with an OK button
        """Open a centered message window with an acknowledgement button."""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.transient(self.root)
        window.resizable(False, False)
        ttk.Label(window, text=message, wraplength=320, justify="left", padding=20).pack()
        ttk.Button(window, text="OK", command=window.destroy).pack(pady=(0, 15))

        # put it in the middle of the main window
        window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - window.winfo_height()) // 2
        window.geometry(f"+{x}+{y}")

    def askYesNo(self, title, message):
        """Ask for confirmation and return the user response."""
        return messagebox.askyesno(title, message, parent=self.root)

    def exitApp(self):
        """Destroy the application window and end the GUI session."""
        self.root.destroy()


def guiMain():
    # the GUI's own entry point, the same setup chain as main.py
    """Initialize shared services and run the graphical application."""
    try:
        database = Database(DATA_PATH)
        repo = StudentRepository.createStudentRepository(database)
    except (ValueError, KeyError, OSError) as error:
        # ASSUMPTION: same as main.py, load() does not handle a damaged file.
        # REPLACE LATER if Shiva handles it himself.
        print(f"Could not load the students file: {error}")
        return

    validator = Validator(repo)
    generator = IDGenerator(repo)

    GUIUniApp(repo, validator, generator).run()


if __name__ == "__main__":
    guiMain()