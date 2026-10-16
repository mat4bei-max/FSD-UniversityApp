# UniversityApp

Self-enrolment system for a local university (UTS 32555 Fundamentals of Software Development, Assessment 1, Group Cmp1-07).
Implemented as a command-line app (`CLIUniApp`) with an optional GUI challenge (`GUIUniApp`).

## Features

- **University menu:** choose Admin, Student or Exit.
- **Student:** register (email and password are validated), login, change password.
- **Subject enrolment:** enrol in up to 4 subjects, remove a subject, show subjects with mark and grade.
  Each subject gets a random mark (25–100); a student passes if the average mark is >= 50.
- **Admin (no login required):** show all students, group by grade, partition into PASS/FAIL, remove a student by ID, clear the database.
- **Persistence:** all student data is stored in `students.data` (created automatically if missing).

## Team

Mathis Arthur Beissner, Shivakumar Kothapally, Siddharth Shanbhag, Varun Pocham
