from __future__ import annotations

from copy import deepcopy

from university_app.src.system.student import Student
from university_app.src.database.database import Database

class StudentRepository:
    """
    Repository of students in the university system.
    Initialize with createStudentRepository(database) function.
    """
    def __init__(
            self,
            database: Database,
            students: list[Student]
        ):
        """ Initialize a new StudentRepository instance. """
        self._database = database
        self._students = students

    @classmethod
    def createStudentRepository(
        cls,
        database: Database
    ) -> StudentRepository:
        """
        Create a new StudentRepository instance.
        Loads the list of students from the database and initializes the repository with it.
        """
        students = database.load() 
        return cls(database=database, students=students)

    # Get functions
    def getStudent(self, student_id: str) -> Student:
        """Return a student by ID."""
        for student in self._students:
            if student.student_id == student_id:
                return deepcopy(student)

        raise ValueError(f"Student with ID {student_id} not found.")

    def getStudents(self) -> list[Student]:
        """Return all students."""
        return deepcopy(self._students)

    # Set functions
    def addStudent(self, student: Student) -> None:
        """ Add a new student to the repository. """
        if student.student_id in self.getAllStudentIDs():
            raise ValueError(
                f"Student with ID {student.student_id} already exists."
            )
    
        updated_students = deepcopy(self._students)
        updated_students.append(deepcopy(student))
        self._database.save(updated_students)
        self._students = updated_students

    def removeStudent(self, student_id: str) -> None:
        """ Remove a student from the repository. """
        for index, student in enumerate(self._students):
            if student.student_id == student_id:
                updated_students = deepcopy(self._students)
                del updated_students[index]

                self._database.save(updated_students)
                self._students = updated_students
                return

        raise ValueError(f"Student with ID {student_id} not found.")

    def updateStudent(self, updated_student: Student) -> None:
        """Update an existing student and save the changes in the database."""
        for index, student in enumerate(self._students):
            if student.student_id == updated_student.student_id:
                updated_students = deepcopy(self._students)
                updated_students[index] = deepcopy(updated_student)
                self._database.save(updated_students)
                self._students = updated_students
                return

        raise ValueError(f"Student with ID {updated_student.student_id} not found.")

    def clearAllStudents(self) -> None:
        """ Remove all students from the repository. """
        self._database.save([])
        self._students = []

    # Utility functions
    def getAllStudentIDs(self) -> list[str]:
        """
        Returns a list of all student IDs in the repository.
        Intended to be used by Generator for creating unique student IDs.
        """
        student_ids = list()
        for student in self._students:
            student_ids.append(student.student_id)

        return student_ids

    def getAllSubjectIDs(self) -> list[str]:
        """
        Returns a list of all subject IDs in the repository.
        Intended to be used by Generator for creating unique subject IDs.
        """
        subject_ids = list()
        for student in self._students:
            for subject in student.subjects:
                subject_ids.append(subject.subject_id)

        return subject_ids

    def getAllEmails(self) -> list[str]:
        """
        Returns a list of all student emails in the repository.
        Intended to be used by Validator for checking if student is already registered.
        """
        emails = list()
        for student in self._students:
            emails.append(student.email)

        return emails