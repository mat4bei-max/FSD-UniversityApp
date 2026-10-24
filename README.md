# UniversityApp

Self-enrolment system for a local university (UTS 32555 Fundamentals of Software Development, Assessment 1, Group Cmp1-07).
Implemented as a command-line app (`CLIUniApp`) with an optional GUI challenge (`GUIUniApp`).

## Features

- **University menu:** choose Admin, Student or Exit.
- **Student:** register (email and password are validated), login, change password.
- **Subject enrolment:** enrol in up to 4 subjects, remove a subject, show subjects with mark and grade.
  Each subject gets a random mark (25–100); a student passes if the average mark is >= 50.
- **Admin (no login required):** show all students, group by grade, partition into PASS/FAIL, remove a student by ID, clear the database.
- **Persistence:** all student data is stored in `university_app/data/students.json` during development (JSON list of students). For submission, rename/use `students.data` with the same JSON content — `Database(path)` accepts either filename.
- **Shiva (model utils):** `Database` (load/save/clear), `Validator` (email/password/login), `IDGenerator` (unique student/subject IDs). Controllers should use these via `StudentRepository`; do not open the file directly.

## Team

Mathis Arthur Beissner, Shivakumar Kothapally, Siddharth Shanbhag, Varun Pocham
