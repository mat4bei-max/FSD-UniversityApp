from __future__ import annotations

from src.system.student import Student

class Database:
    """
    Database for storing student information in the university system.
    
    """
    def __init__(self):
        pass

    def load(self) -> list[Student]:
<<<<<<< Updated upstream
        pass
=======
        """
        Load all students from the file.
        Creates an empty file and returns [] if the file does not exist or is empty.
        """
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._write_json([])
            return []

        raw = self._path.read_text(encoding="utf-8").strip()
        if not raw:
            return []

        rows = json.loads(raw)
        students: list[Student] = []
        for row in rows:
            subjects = [
                Subject(
                    subject_id=str(subject["subject_id"]),
                    mark=int(subject["mark"]),
                    grade=str(subject["grade"]),
                )
                for subject in row.get("subjects", [])
            ]
            students.append(
                Student(
                    student_id=str(row["student_id"]),
                    name=str(row["name"]),
                    email=str(row["email"]),
                    password=str(row["password"]),
                    subjects=subjects,
                )
            )
        return students
>>>>>>> Stashed changes

    def save(self, students: list[Student]) -> None:
        pass