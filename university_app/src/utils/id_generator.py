from __future__ import annotations

from university_app.src.system.student_repository import StudentRepository

class IDGenerator:
    """ Utility class for generating unique IDs for students and subjects. """

    def __init__(self, student_repository: StudentRepository) -> None:
        """ Initialize the IDGenerator instance. """
        self._student_repository = student_repository

    def generateStudentId(self) -> int:
        """ Generate a new, unique student ID. """
        self._student_repository.getAllStudentIDs()
        pass

    def generateSubjectId(self) -> int:
        """ Generate a new, unique subject ID. """
        self._student_repository.getAllSubjectIDs()
        pass
