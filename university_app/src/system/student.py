from __future__ import annotations

from copy import deepcopy

from university_app.src.system.subject import Subject

class Student:
    """
    Student in the university system.
    """
    def __init__(
            self,
            student_id: str,
            name: str,
            email: str,
            password: str,
            subjects: list[Subject]
        ):
        """ Initialize a new Student instance. """

        expected_name = self.get_name_from_email(email)
        if name.strip().casefold() != expected_name.casefold():
            raise ValueError("Name does not match the name derived from the email.")
        if len(subjects) > 4:
            raise ValueError("A student cannot have more than 4 subjects.")
        
        self.student_id = student_id
        self.name = expected_name
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

    def removeSubject(self, subject_id: str) -> None:
        """ Remove a subject from the student's list of subjects. """
        for subject in self.subjects:
            if subject.subject_id == subject_id:
                self.subjects.remove(subject)
                return

        raise ValueError(f"Subject with ID {subject_id} not found.")

    def getSubjects(self) -> list[Subject]:
        """Get the list of subjects for the student."""
        return deepcopy(self.subjects)

    def changePassword(self, new_password: str) -> None:
        """Change the student's password."""
        self.password = new_password

    @staticmethod
    def get_name_from_email(email: str) -> str:
        """Get the student's name based on their email."""
        names = email.split('@')[0]
        
        if '.' in names:
            firstname, lastname = names.split('.', 1)
        else:
            firstname, lastname = names, ""

        name = " ".join([firstname.capitalize(), lastname.capitalize()])

        return name

