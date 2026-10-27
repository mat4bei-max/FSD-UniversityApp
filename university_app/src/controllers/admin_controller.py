from pathlib import Path

from university_app.src.database.database import Database
from university_app.src.system.student_repository import StudentRepository
from university_app.src.system.subject import Subject


class AdminController:
    def __init__(self, repo):
        """Initialize the instance and its dependencies."""
        self.repo = repo

    def run(self):
        # Admins enter directly: no login is required.
        """Run the menu until the user chooses to exit."""
        while True:
            choice = input(
                "    Admin System (c/g/p/r/s/x): "
            ).strip().lower()

            try:
                if choice == "s":
                    self.show_students()
                elif choice == "g":
                    self.group_students()
                elif choice == "p":
                    self.partition_students()
                elif choice == "r":
                    self.remove_student()
                elif choice == "c":
                    self.clear_students()
                elif choice == "x":
                    return
                else:
                    print("    Invalid choice. Enter c, g, p, r, s, or x.")
            except (ValueError, OSError) as error:
                print(f"    {error}")

    def average_mark(self, student):
        """Return the average subject mark, or None when no subjects exist."""
        subjects = student.getSubjects()
        if not subjects:
            return None
        # Provisional rule: average currently enrolled subjects, even if fewer
        # than four. Confirm that interpretation with the tutor.
        return sum(subject.mark for subject in subjects) / len(subjects)

    def student_summary(self, student):
        """Format the student ID, average mark, and grade for display."""
        average = self.average_mark(student)
        if average is None:
            return f"{student.name} :: {student.student_id} -- no subjects"
        grade = Subject.calculateGrade(average)
        return (
            f"{student.name} :: {student.student_id}"
            f" --> GRADE: {grade} - MARK: {average:.2f}"
        )

    def show_students(self):
        """Display all students currently stored in the repository."""
        students = self.repo.getStudents()
        print("    Student List")
        if not students:
            print("        < Nothing to Display >")
            return
        for student in students:
            print(
                f"    {student.name} :: {student.student_id}"
                f" --> Email: {student.email}"
            )

    def group_students(self):
        """Display students grouped by their average grade."""
        students = self.repo.getStudents()
        print("    Grade Grouping")
        if not students:
            print("        < Nothing to Display >")
            return

        groups = {grade: [] for grade in ("Z", "P", "C", "D", "HD", "UNGRADED")}
        for student in students:
            average = self.average_mark(student)
            grade = "UNGRADED" if average is None else Subject.calculateGrade(average)
            groups[grade].append(self.student_summary(student))

        for grade, entries in groups.items():
            if entries:
                print(f"    {grade} --> [{', '.join(entries)}]")

    def partition_students(self):
        """Display students grouped by pass, fail, or unclassified status."""
        print("    PASS/FAIL Partition")
        groups = {"FAIL": [], "PASS": [], "UNCLASSIFIED": []}

        for student in self.repo.getStudents():
            average = self.average_mark(student)
            if average is None:
                status = "UNCLASSIFIED"
            elif average >= 50:
                status = "PASS"
            else:
                status = "FAIL"
            groups[status].append(self.student_summary(student))

        for status, entries in groups.items():
            if status != "UNCLASSIFIED" or entries:
                print(f"    {status} --> [{', '.join(entries)}]")

    def remove_student(self):
        """Validate an entered student ID and remove the matching account."""
        entered_id = input("    Remove by ID: ").strip()
        if not entered_id.isascii() or not entered_id.isdigit():
            raise ValueError("Student ID must be a number.")

        if not 1 <= int(entered_id) <= 999999:
            raise ValueError("Student ID must be between 000001 and 999999.")

        try:
            self.repo.removeStudent(entered_id)
        except ValueError:
            raise ValueError(f"Student {entered_id} does not exist") from None
        print(f"    Removing Student {entered_id} Account")

    def clear_students(self):
        """Clear all student accounts after confirmation."""
        print("    Clearing students database")
        answer = input(
            "    Are you sure you want to clear the database (Y)ES/(N)O: "
        ).strip().lower()

        if answer in ("y", "yes"):
            self.repo.clearAllStudents()
            print("    Students data cleared")
        elif answer in ("n", "no"):
            return
        else:
            print("    Invalid answer. Enter Y or N. Nothing was cleared.")


if __name__ == "__main__":
    data_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "students.data"
    )

    database = Database(data_path)
    repo = StudentRepository.createStudentRepository(database)
    controller = AdminController(repo)
    controller.run()
