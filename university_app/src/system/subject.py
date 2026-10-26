from __future__ import annotations

import random

class Subject:
    """ Subject in the university system. """
    def __init__(
            self,
            subject_id: str,
            mark: int, 
            grade: str
        ):
        """ Initialize a new Subject instance. """

        if not self.validateMark(mark):
            raise ValueError(f"Invalid mark: {mark}")
        if not self.validateGrade(grade, mark):
            raise ValueError(f"Invalid grade: {grade} for mark: {mark}")
        
        self.subject_id = subject_id
        self.mark = mark
        self.grade = grade

    @staticmethod
    def generateSubjectMark() -> int:
        """ Generate a new mark for the subject. """
        return random.randint(25, 100)

    @staticmethod
    def calculateGrade(mark: int) -> str:
        """ Calculate the grade based on a mark. """
        if mark < 50:
            grade = "Z"
        elif 50 <= mark < 65:
            grade = "P"
        elif 65 <= mark < 75:
            grade = "C"
        elif 75 <= mark < 85:
            grade = "D"
        else:
            grade = "HD"

        return grade

    @staticmethod
    def validateMark(mark: int) -> bool:
        """ Validate if the mark is within the acceptable range. """
        return 25 <= mark <= 100

    @staticmethod
    def validateGrade(grade: str, mark: int) -> bool:
        """ Validate if the grade corresponds to the mark. """
        calculated_grade = Subject.calculateGrade(mark)
        return grade == calculated_grade

