from __future__ import annotations

from university_app.src.system.student_repository import StudentRepository

class Validator:
    """ Utility class for validating ID's and credentials. """

    def __init__(self, student_repository: StudentRepository) -> None:
        """ Initialize the Validator instance. """
        self._student_repository = student_repository