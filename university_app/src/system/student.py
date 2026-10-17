from __future__ import annotations

from university_app.src.system.subject import Subject

class Student:
    """
    Student in the university system.
    """
    def __init__(
            self,
            student_id: int,
            name: str,
            email: str,
            password: str,
            subjects: list[Subject]
        ):
        """ Initialize a new Student instance. """
        self.student_id = student_id
        self.name = name
        self.email = email
        self.password = password
        self.subjects = subjects

    def addSubject(self, subject: Subject) -> None:
        """
        Add a new subject to the student's list of subjects.
        Validates if maximum number of subjects (4) is reached before adding a new one.
        """
        # Check if the student has reached the maximum number of subjects.
        if len(self.subjects) >= 4:
            raise ValueError("Maximum number of subjects (4) reached.")

        self.subjects.append(subject)

    def removeSubject(self, subject_id: int) -> None:
        """ Remove a subject from the student's list of subjects. """
        for subject in self.subjects:
            if subject.subject_id == subject_id:
                self.subjects.remove(subject)
                return

        raise ValueError(f"Subject with ID {subject_id} not found.")

    def getSubjects(self) -> list[Subject]:
        """Get the list of subjects for the student."""
        return self.subjects

    def changePassword(self, new_password: str) -> None:
        """Change the student's password."""
        self.password = new_password

