from __future__ import annotations

import re

from university_app.src.system.student import Student
from university_app.src.system.student_repository import StudentRepository


class Validator:
    """Utility class for validating credentials against assignment rules."""

    EMAIL_PATTERN = re.compile(r"^[A-Za-z]+\.[A-Za-z]+@university\.com$")
    # Starts with uppercase, at least five letters total, then three or more digits.
    PASSWORD_PATTERN = re.compile(r"^[A-Z][A-Za-z]{4,}\d{3,}$")

    def __init__(self, student_repository: StudentRepository) -> None:
        """Initialize the Validator instance."""
        self._student_repository = student_repository

    def validateEmail(self, email: str) -> None:
        """Raise ValueError if the email does not match firstname.lastname@university.com."""
        if not self.EMAIL_PATTERN.fullmatch(email):
            raise ValueError(
                "Invalid email. Use firstname.lastname@university.com"
            )

    def validatePassword(self, password: str) -> None:
        """
        Raise ValueError if the password does not meet the required pattern:
        uppercase start, at least five letters, then three or more digits.
        """
        if not self.PASSWORD_PATTERN.fullmatch(password):
            raise ValueError(
                "Invalid password. Start with an uppercase letter, "
                "use at least five letters, then three or more digits."
            )

    def ensureNewEmail(self, email: str) -> None:
        """Raise ValueError if the email is already registered."""
        if email in self._student_repository.getAllEmails():
            raise ValueError(f"Student already exists: {email}")

    def login(self, email: str, password: str) -> Student:
        """
        Return the matching student if email and password are correct.
        Raises ValueError when credentials do not match a stored student.
        """
        for student in self._student_repository.getStudents():
            if student.email == email and student.password == password:
                return student
        raise ValueError("Incorrect email or password.")
