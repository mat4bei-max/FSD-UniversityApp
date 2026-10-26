from university_app.src.system.subject import Subject


class SubjectController:
    def __init__(self, repo, validator, generator):
        self.repo = repo
        self.validator = validator
        self.generator = generator

    def run(self, student_id):
        while True:
            choice = input(
                "        Student Course Menu (c/e/r/s/x): "
            ).strip().lower()

            try:
                if choice == "e":
                    subject, count = self.enrol(student_id)
                    print(f"        Enrolling in Subject-{subject.subject_id}")
                    print(
                        f"        You are now enrolled in "
                        f"{count} out of 4 subjects"
                    )

                elif choice == "r":
                    self.remove_subject(student_id)

                elif choice == "s":
                    self.show_subjects(student_id)

                elif choice == "c":
                    self.change_password(student_id)

                elif choice == "x":
                    return

                else:
                    print("        Invalid choice. Enter c, e, r, s, or x.")

            except (ValueError, OSError) as error:
                print(f"        {error}")

    def enrol(self, student_id):
        # Fetch a copy of the student's current record.
        student = self.repo.getStudent(student_id)

        # Create a subject using the team's shared classes.
        subject_id = self.generator.generateSubjectId()
        mark = Subject.generateSubjectMark()
        grade = Subject.calculateGrade(mark)

        subject = Subject(
            subject_id=subject_id,
            mark=mark,
            grade=grade
        )

        # Student checks the four-subject limit.
        try:
            student.addSubject(subject)
        except ValueError as error:
            if str(error) == "Maximum number of subjects (4) reached.":
                raise ValueError("Students are allowed to enrol in 4 subjects only") from None
            raise

        # Save the changed student through the repository.
        self.repo.updateStudent(student)

        return subject, len(student.getSubjects())

    def remove_subject(self, student_id):
        entered_id = input("        Remove Subject by ID: ").strip()

        if not entered_id.isascii() or not entered_id.isdigit():
            raise ValueError("Subject ID must be a number.")

        if not 1 <= int(entered_id) <= 999:
            raise ValueError("Subject ID must be between 001 and 999.")

        student = self.repo.getStudent(student_id)
        student.removeSubject(entered_id)
        self.repo.updateStudent(student)

        print(f"        Dropping Subject-{entered_id}")
        print(
            f"        You are now enrolled in "
            f"{len(student.getSubjects())} out of 4 subjects"
        )

    def show_subjects(self, student_id):
        student = self.repo.getStudent(student_id)
        subjects = student.getSubjects()

        print(f"        Showing {len(subjects)} subjects")

        for subject in subjects:
            print(
                f"        [ Subject::{subject.subject_id}"
                f" -- mark = {subject.mark}"
                f" -- grade = {subject.grade} ]"
            )

    def change_password(self, student_id):
        print("        Updating Password")

        new_password = input("        New Password: ")
        self.validator.validatePassword(new_password)

        while True:
            confirmation = input("        Confirm Password: ")

            if confirmation == new_password:
                break

            print("        Password does not match - try again")

        student = self.repo.getStudent(student_id)
        student.changePassword(new_password)
        self.repo.updateStudent(student)
