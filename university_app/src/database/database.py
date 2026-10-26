from __future__ import annotations

import json
from pathlib import Path

from university_app.src.system.student import Student
from university_app.src.system.subject import Subject


class Database:
    """
    Database for storing student information in the university system.
    Reads and writes Student objects to a local JSON file (students.data / students.json).
    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the database with the path to the students file."""
        self._path = Path(path)

    def load(self) -> list[Student]:
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

    def save(self, students: list[Student]) -> None:
        """Write the full list of students to the file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "student_id": student.student_id,
                "name": student.name,
                "email": student.email,
                "password": student.password,
                "subjects": [
                    {
                        "subject_id": subject.subject_id,
                        "mark": subject.mark,
                        "grade": subject.grade,
                    }
                    for subject in student.subjects
                ],
            }
            for student in students
        ]
        self._write_json(payload)

    def clear(self) -> None:
        """Clear all students from the file. The file itself remains on disk."""
        self.save([])

    def _write_json(self, payload: list) -> None:
        self._path.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )
