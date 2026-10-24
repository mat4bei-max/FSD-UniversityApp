from __future__ import annotations

import random

from university_app.src.system.student_repository import StudentRepository


class IDGenerator:
    """Utility class for generating unique IDs for students and subjects."""

    STUDENT_ID_MIN = 1
    STUDENT_ID_MAX = 999999
    SUBJECT_ID_MIN = 1
    SUBJECT_ID_MAX = 999

    def __init__(self, student_repository: StudentRepository) -> None:
        """Initialize the IDGenerator instance."""
        self._student_repository = student_repository

    def generateStudentId(self) -> int:
        """Generate a new, unique student ID (000001–999999)."""
        used = set(self._student_repository.getAllStudentIDs())
        while True:
            student_id = random.randint(self.STUDENT_ID_MIN, self.STUDENT_ID_MAX)
            if student_id not in used:
                return student_id

    def generateSubjectId(self) -> int:
        """Generate a new, unique subject ID (001–999)."""
        used = set(self._student_repository.getAllSubjectIDs())
        while True:
            subject_id = random.randint(self.SUBJECT_ID_MIN, self.SUBJECT_ID_MAX)
            if subject_id not in used:
                return subject_id
