from __future__ import annotations

from university_app.src.system.student_repository import StudentRepository

class IDGenerator:
    """ Utility class for generating unique IDs for students and subjects. """

    def __init__(self, student_repository: StudentRepository) -> None:
        """ Initialize the IDGenerator instance. """
        self._student_repository = student_repository

<<<<<<< Updated upstream
    def generateStudentId(self) -> int:
        """ Generate a new, unique student ID. """
        self._student_repository.getAllStudentIDs()
        pass

    def generateSubjectId(self) -> int:
        """ Generate a new, unique subject ID. """
        self._student_repository.getAllSubjectIDs()
        pass
=======
    def generateStudentId(self) -> str:
        """Generate a unique student ID (000001–999999)."""
        used = set(self._student_repository.getAllStudentIDs())

        while True:
            student_id = f"{random.randint(self.STUDENT_ID_MIN, self.STUDENT_ID_MAX):06d}"

            if student_id not in used:
                return student_id

    def generateSubjectId(self) -> str:
        """Generate a unique subject ID (001–999)."""
        used = set(self._student_repository.getAllSubjectIDs())

        while True:
            subject_id = f"{random.randint(self.SUBJECT_ID_MIN, self.SUBJECT_ID_MAX):03d}"

            if subject_id not in used:
                return subject_id
>>>>>>> Stashed changes
